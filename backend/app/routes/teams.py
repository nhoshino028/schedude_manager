from flask import Blueprint, jsonify

from app.db import get_db
from app.schemas.teams import Team


teams_bp = Blueprint("teams", __name__)


@teams_bp.get("/teams")
def list_teams():
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT id, team_code, name, created_at, updated_at ORDER BY id"  #idのところ読み込めてない column "id" does not exist
        )
        rows = cur.fetchall()

    items = [
        Team.model_validate(row).model_dump(mode="json", by_alias=True)
        for row in rows
    ]

    return jsonify(items), 200