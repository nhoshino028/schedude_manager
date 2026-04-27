"""
予定 (schedules) リソースのエンドポイントを集約する Blueprint。

役割:
    /schedules パス配下の CRUD を扱う。Phase2 の本模範解答では
    POST /schedules のみお手本として完全実装し、GET / PUT / DELETE は
    受講者課題として TODO コメントだけ残す。

公開物:
    schedules_bp: Flask Blueprint。create_app() が register_blueprint で
    登録する。Phase2 完了時点では POST のみハンドラあり、GET / PUT /
    DELETE は受講者が後から実装する想定。

呼び出し関係:
    - 上流: app/__init__.py の create_app() (Task 8 で登録)
    - 下流:
        - app.db.get_db() で psycopg 接続を取得
        - app.schemas.schedules の ScheduleCreateRequest /
          ScheduleResponse / ScheduleUpdateRequest
        - app.errors.ConflictError (FK 違反時) /
          NotFoundError (受講者の PUT/DELETE で利用)

学習ポイント (POST のお手本で見せたい技術):
    1. request.get_json で生 JSON を取得
    2. ScheduleCreateRequest.model_validate でバリデーション
       (失敗時は pydantic.ValidationError -> 400 ハンドラ)
    3. with db.cursor() で INSERT ... RETURNING * を実行
    4. psycopg.errors.ForeignKeyViolation を try/except で捕捉し
       ConflictError に変換 -> 409
    5. db.commit() / db.rollback() でトランザクション境界を明示
    6. ScheduleResponse.model_dump(mode="json", by_alias=True) で 201 + Location
       (mode="json" が無いと time / datetime が JSON 化できず 500 になる)
"""

from flask import Blueprint, jsonify, request, url_for
from psycopg import errors as pg_errors

from app.db import get_db
from app.errors import ConflictError
from app.schemas.schedules import ScheduleCreateRequest, ScheduleResponse


schedules_bp = Blueprint("schedules", __name__)


# =============================================================================
# お手本: POST /schedules (完全実装)
# =============================================================================
@schedules_bp.post("/schedules")
def create_schedule():
    """
    POST /schedules - 予定登録 (仕様書 §4.2)。

    処理:
        1. リクエストボディ JSON を request.get_json(silent=True) で取得。
           不正 JSON や空ボディは {} にフォールバックさせ、pydantic 側で
           「必須欠落の VALIDATION_ERROR」を吐く流れにする。
        2. ScheduleCreateRequest.model_validate(payload) でバリデーション。
           - 必須 (userId / targetDate / statusTypeId) 欠落時:
             ValidationError -> errors.py が 400 にマップ。
           - startTime > endTime のクロスフィールド違反:
             ValidationError (model_validator) -> 同上。
        3. psycopg 接続を get_db() で取得。
        4. with db.cursor(): INSERT ... RETURNING * で行を作って取り出す。
           - 名前付きプレースホルダ (%(name)s) で body.model_dump() の
             snake_case dict をそのまま渡す。
        5. ForeignKeyViolation を捕捉した場合:
           - db.rollback() でトランザクションを巻き戻す。
           - ConflictError を raise -> errors.py が 409 にマップ。
        6. 正常時 db.commit() で確定。
        7. RETURNING で取得した行を ScheduleResponse.model_validate して
           model_dump(mode="json", by_alias=True) で camelCase + JSON 互換型に変換。
           mode="json" を付けないと time / date / datetime が Python オブジェクト
           のまま残り、flask.jsonify が TypeError で落ちて 500 になる。
        8. Location ヘッダ "/schedules/{id}" を付与し 201 で返却。

    引数:
        なし。リクエストボディから JSON を読み取る。

    戻り値:
        201 Created
            ボディ: ScheduleResponse の camelCase JSON
            ヘッダ: Location: /schedules/{id}
        400 (errors.py に委譲): バリデーションエラー
        409 (errors.py に委譲): FK 違反 (userId / statusTypeId 不存在)

    暗黙的に利用するもの:
        - flask.g 経由の psycopg 接続 (get_db / close_db のサイクル)
        - DB 定義書 §共通方針 (line 71) に従い、created_at / updated_at は
          アプリ側で SQL の now() を渡して設定する (DB に DEFAULT は持たない)。
          INSERT 文で明示的に now(), now() を渡している。
        - errors.py の register_error_handlers が ValidationError /
          ConflictError を共通形式 JSON に変換する
    """
    # 1. JSON ボディ取得。silent=True により JSON パース失敗で例外を出さず
    #    None を返す。{} にフォールバックすることで pydantic に
    #    「全フィールド欠落」として処理させる (= 必須欠落の 400)。
    payload = request.get_json(silent=True) or {}

    # 2. pydantic でバリデーション。失敗時は ValidationError が raise され、
    #    errors.py の @app.errorhandler(ValidationError) が 400 + details を返す。
    body = ScheduleCreateRequest.model_validate(payload)

    # 3. DB 接続取得 (リクエストスコープ; close は teardown で自動)。
    db = get_db()

    try:
        # 4. INSERT ... RETURNING で挿入後の行をそのまま取得する。
        #    名前付きプレースホルダ %(name)s は psycopg 3 の dict 渡し記法。
        #    body.model_dump() は snake_case の dict を返す (by_alias=False 既定)。
        #    created_at / updated_at は DB 定義書 §共通方針 (line 71) に従い
        #    アプリ側で SQL の now() を渡す (DB に DEFAULT を持たせない設計)。
        with db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO schedules
                    (user_id, target_date, status_type_id, start_time, end_time, comment,
                     created_at, updated_at)
                VALUES
                    (%(user_id)s, %(target_date)s, %(status_type_id)s,
                     %(start_time)s, %(end_time)s, %(comment)s,
                     now(), now())
                RETURNING id, user_id, target_date, status_type_id,
                          start_time, end_time, comment, created_at, updated_at
                """,
                body.model_dump(),
            )
            # row_factory=dict_row なので fetchone() は 1 行を dict で返す。
            row = cur.fetchone()
        # 5. 正常時 commit (autocommit=False のため明示的に必要)。
        db.commit()

    except pg_errors.ForeignKeyViolation as e:
        # 6. user_id / status_type_id が存在しない FK 値だと PostgreSQL が
        #    23503 (foreign_key_violation) を返す。psycopg がこれを例外化する。
        #    ロールバック後、教育目的のメッセージ付き ConflictError に変換し、
        #    errors.py が 409 + 仕様書 §1 形式 JSON にマップする。
        db.rollback()
        raise ConflictError(
            "foreign key violation: userId or statusTypeId does not exist"
        ) from e

    # 7. レスポンスを pydantic で整形 (snake -> camel + JSON 互換型へ変換)。
    #    mode="json" を指定することで、pydantic が date / time / datetime を
    #    ISO 8601 風の文字列に変換する (例: time -> "HH:MM:SS"、datetime -> RFC3339)。
    #    これを指定しないと flask.jsonify が time オブジェクトを直接渡されて
    #    "TypeError: Object of type time is not JSON serializable" を出す。
    response_body = ScheduleResponse.model_validate(row).model_dump(
        mode="json", by_alias=True
    )

    # 8. Location ヘッダで作成リソースの URL を返す。
    #    url_for("schedules.create_schedule") は POST 自身のルート (/schedules)
    #    を返すので、それに /<id> を連結して /schedules/<id> を作る。
    #    受講者が後で PUT/DELETE を実装した暁には、url_for("schedules.update_schedule",
    #    id=row["id"]) のように書き換えるとさらに堅牢になる旨を学習ヒントとして残す。
    headers = {"Location": url_for("schedules.create_schedule") + f"/{row['id']}"}

    return jsonify(response_body), 201, headers


# =============================================================================
# 受講者 TODO: GET /schedules (仕様書 §4.1)
# =============================================================================
# 実装手順 (受講者向け):
#   1. クエリパラメータを request.args.get("date") / .get("userId") /
#      .get("from") / .get("to") で取得する。
#   2. バリデーション:
#      - "date" と "from"/"to" は同時指定不可 (両方あれば 400 を返す)。
#      - "from" と "to" はセット (片方だけなら 400)。
#      バリデーション NG の場合、ValidationError を raise するか、
#      手動で {"code": "VALIDATION_ERROR", ...} を返す。
#   3. 動的に WHERE 句を組み立て、psycopg のプレースホルダで安全に渡す。
#      文字列連結で SQL を組まないこと (CLAUDE.md 強制ルール)。
#   4. fetchall() の結果を ScheduleResponse のリストにし、
#      model_dump(by_alias=True) で jsonify。
#   5. 200 で返す。
#
# お手本: 上記 create_schedule の "with db.cursor()" 〜 "jsonify" の流れ。
#
# @schedules_bp.get("/schedules")
# def list_schedules():
#     ...

# =============================================================================
# 受講者 TODO: PUT /schedules/{id} (仕様書 §4.3)
# =============================================================================
# 実装手順 (受講者向け):
#   1. app/schemas/schedules.py の ScheduleUpdateRequest を完成させる。
#   2. ScheduleUpdateRequest.model_validate(payload) でバリデーション。
#   3. UPDATE ... WHERE id = %(id)s RETURNING * で行を更新。
#   4. fetchone() の結果が None (= 行が存在しなかった) ならば
#      app.errors.NotFoundError を raise (-> 404)。
#   5. 200 で ScheduleResponse を返す。
#
# お手本: 上記 create_schedule の try/commit/rollback の流れ。
# UPDATE 用の SQL は INSERT を参考に書き換える。

# =============================================================================
# 受講者 TODO: DELETE /schedules/{id} (仕様書 §4.4)
# =============================================================================
# 実装手順 (受講者向け):
#   1. DELETE FROM schedules WHERE id = %(id)s RETURNING id を実行。
#   2. fetchone() が None なら NotFoundError (404)。
#   3. 成功時は ("", 204) を返す (jsonify せず空ボディ + 204 No Content)。
#   4. db.commit() を忘れない。
#
# お手本: create_schedule の commit/rollback と errors.NotFoundError の使い方。
