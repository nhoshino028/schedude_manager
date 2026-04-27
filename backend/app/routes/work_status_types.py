"""
GET /work-status-types エンドポイントを提供する Blueprint。

役割:
    勤務区分マスタ (work_status_types テーブル) の全件取得を行う。
    Phase2 のお手本完全実装の 1 つ目。最小構成で
    「DB 接続 → SELECT → pydantic → JSON」の流れを示す教材。

公開物:
    work_status_types_bp: Flask Blueprint。create_app() が
    register_blueprint で登録する。

呼び出し関係:
    - 上流: app/__init__.py の create_app() (Task 8 で登録)
    - 下流:
        - app.db.get_db() で psycopg 接続を取得
        - app.schemas.work_status_types.WorkStatusType でレスポンス整形

学習ポイント (受講者向け):
    1. Blueprint の生成と URL マッピング (@bp.get)
    2. get_db() で接続を取り、with cursor として SELECT
    3. row_factory=dict_row により fetchall() 戻り値が
       [{"id": 1, "status_code": "OFFICE", ...}, ...] となる
    4. WorkStatusType.model_validate(row) で型検証
    5. .model_dump(mode="json", by_alias=True) で camelCase 化 + JSON 互換型へ
       (本ファイルのスキーマには date / time / datetime が含まれないため
        mode="json" は実質 no-op だが、お手本としての記法統一のため明示する)
    6. jsonify(list) でレスポンス JSON 配列を返却
"""

from flask import Blueprint, jsonify

from app.db import get_db
from app.schemas.work_status_types import WorkStatusType


# Blueprint 名は "work_status_types"。url_prefix は無し。
# 第二引数 __name__ は Flask の要求仕様 (テンプレート/静的ファイルの起点)。
work_status_types_bp = Blueprint("work_status_types", __name__)


@work_status_types_bp.get("/work-status-types")
def list_work_status_types():
    """
    GET /work-status-types - 勤務区分マスタ全件取得 (仕様書 §3.3)。

    処理:
        1. get_db() で現リクエスト用の psycopg 接続を取得。
        2. with db.cursor() で cursor を開き、ORDER BY id で全行 SELECT。
        3. fetchall() で list[dict] を取得 (row_factory=dict_row のため)。
        4. 各行を WorkStatusType.model_validate(row) で型検証 +
           model_dump(mode="json", by_alias=True) で camelCase + JSON 互換型に変換。
           mode="json" は本リソースには date / time / datetime が無いため実質
           no-op だが、お手本としての記法統一のため明示する (受講者が PUT/DELETE
           など date/time を含むレスポンスをコピペで作ったとき 500 を踏まないため)。
        5. list を jsonify して 200 OK で返却。

    引数:
        なし。クエリパラメータ・リクエストボディは読み取らない。

    戻り値:
        flask.Response (200 OK, application/json)。
        ボディ: [{"id": 1, "statusCode": "OFFICE", "statusName": "出社"}, ...]

    暗黙的に利用するもの:
        - flask.g (DB 接続のキャッシュ場所、get_db 内部で利用)。
        - DB 接続のクローズは teardown_appcontext (close_db) に委譲。
        - work_status_types テーブルが Phase1 のマスタ投入で 6 行ある前提。
    """
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            # ORDER BY id でマスタ投入順 (= 仕様書の例の並び順) を保証する。
            # 教育目的の SQL なので JOIN や WHERE は無し、最小の SELECT で示す。
            "SELECT id, status_code, status_name FROM work_status_types ORDER BY id"
        )
        # dict_row なので [{"id": 1, "status_code": "OFFICE", "status_name": "出社"}, ...]
        rows = cur.fetchall()

    # WorkStatusType に投入することで、(教育目的で) 型検証と
    # camelCase 変換を pydantic に任せる。dict 直接 jsonify でも
    # 動くが、お手本としてレスポンスにも pydantic を通す体裁を採る。
    # mode="json" は本リソースには date/time/datetime が無いため実質 no-op だが、
    # お手本記法統一 (schedules.py と同じ書き方) のため明示する。
    items = [
        WorkStatusType.model_validate(row).model_dump(mode="json", by_alias=True)
        for row in rows
    ]
    return jsonify(items), 200
