from flask import Blueprint, jsonify

from app.db import get_db
from app.schemas.users import User


users_bp = Blueprint("users", __name__)


@users_bp.get("/users")
def list_users():
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT team, employeeCode, name, team, createdAt ORDER BY id"  #idのところ読み込めてない column "id" does not exist
        )
        rows = cur.fetchall()

    items = [
        User.model_validate(row).model_dump(mode="json", by_alias=True)
        for row in rows
    ]
    return jsonify(items), 200