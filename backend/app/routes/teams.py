"""
チーム関連エンドポイントを提供する Blueprint 雛形 (仕様書 §3.1)。

役割:
    GET /teams を提供する予定の Blueprint。Phase2 模範解答では
    Blueprint 自体は create_app() に登録するが、ハンドラは未実装。
    そのため /teams にアクセスすると Flask 既定の 404 が返る。

公開物:
    teams_bp: Flask Blueprint (ハンドラ未定義)。
    create_app() (Task 8) が register_blueprint で登録する。

呼び出し関係:
    - 上流 (Phase2 で配線): app/__init__.py の create_app()
    - 下流 (受講者が実装):
        - app.db.get_db()
        - app.schemas.teams.Team

受講者向けのヒント:
    - お手本コード: app/routes/work_status_types.py
      (マスタ全件取得の最小例。SELECT -> pydantic -> jsonify)
    - 関連スキーマ: app/schemas/teams.py
    - 仕様書: docs/spec/API仕様書.md §3.1

実装手順 (受講者):
    1. app/schemas/teams.py の Team モデルを完成させる。
    2. teams_bp に @teams_bp.get("/teams") のハンドラを生やす。
    3. db = get_db() で接続を取得し、teams テーブルを SELECT。
       例: SELECT id, team_code, name FROM teams ORDER BY id
    4. 各行を Team.model_validate(row).model_dump(by_alias=True) で
       camelCase 化し、jsonify(list) で 200 を返す。

TODO（受講者）:
    ここに @teams_bp.get("/teams") のハンドラを実装する。
"""

from flask import Blueprint  # noqa: F401  受講者のハンドラで使う

teams_bp = Blueprint("teams", __name__)

# このコメント行より下に @teams_bp.get(...) を生やす。
