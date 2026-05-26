from flask import Blueprint, jsonify

from app.db import get_db
from app.schemas.users import User


users_bp = Blueprint("users", __name__)


@users_bp.get("/users")
def list_users():
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT u.id, u.employee_code, u.name, json_build_object('id', t.id,'teamCode', t.team_code,'name', t.name) AS team, u.created_at FROM users u LEFT JOIN teams t ON u.team_id = t.id ORDER BY u.id ASC;"
        )
        rows = cur.fetchall()

    items = [
        User.model_validate(row).model_dump(mode="json", by_alias=True)
        for row in rows
    ]
    return jsonify(items), 200