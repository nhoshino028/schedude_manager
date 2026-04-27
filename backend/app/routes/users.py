"""
ユーザー関連エンドポイントを提供する Blueprint 雛形 (仕様書 §3.2)。

役割:
    GET /users を提供する予定の Blueprint。Phase2 模範解答では
    Blueprint 自体は create_app() に登録するが、ハンドラは未実装。
    そのため /users にアクセスすると Flask 既定の 404 が返る。

公開物:
    users_bp: Flask Blueprint (ハンドラ未定義)。

呼び出し関係:
    - 上流 (Phase2 で配線): app/__init__.py の create_app()
    - 下流 (受講者が実装):
        - app.db.get_db()
        - app.schemas.users.User (内部で teams.Team をネスト)

受講者向けのヒント:
    - お手本コード: app/routes/work_status_types.py
    - 関連スキーマ: app/schemas/users.py (先に teams.Team を完成させる)
    - 仕様書: docs/spec/API仕様書.md §3.2

実装手順 (受講者):
    1. app/schemas/teams.py の Team を完成させる。
    2. app/schemas/users.py の User (team をネスト) を完成させる。
    3. クエリ teamId を request.args.get("teamId") で取得 (任意)。
    4. SELECT u.id, u.employee_code, u.name, u.created_at,
              t.id AS team_id, t.team_code, t.name AS team_name
       FROM users u JOIN teams t ON u.team_id = t.id
       (teamId 指定時は WHERE u.team_id = %s で絞り込み)
       ORDER BY u.id
    5. 行を User.model_validate (team はネストで再構築) し、
       model_dump(by_alias=True) で jsonify。

TODO（受講者）:
    ここに @users_bp.get("/users") のハンドラを実装する。
"""

from flask import Blueprint  # noqa: F401

users_bp = Blueprint("users", __name__)

# このコメント行より下に @users_bp.get(...) を生やす。
