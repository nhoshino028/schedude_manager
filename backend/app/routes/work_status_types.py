from flask import Blueprint, jsonify

from app.db import get_db
from app.schemas.work_status_types import WorkStatusType


work_status_types_bp = Blueprint("work_status_types", __name__)


@work_status_types_bp.get("/work-status-types")
def list_work_status_types():
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT id, status_code, status_name FROM work_status_types ORDER BY id"
        )
        rows = cur.fetchall()
    
    items = [
        WorkStatusType.model_validate(row).model_dump(mode="json", by_alias=True)
        for row in rows
    ]
    return jsonify(items), 200