from flask import Blueprint, jsonify, request, url_for
from psycopg import errors as pg_errors

from app.db import get_db
from app.errors import ConflictError
from app.errors import NotFoundError
from app.schemas.schedules import ScheduleCreateRequest, ScheduleResponse

schedules_bp = Blueprint("schedules", __name__)
del_schedules_bp = Blueprint("schedules", __name__)


@schedules_bp.post("/schedules")
def create_schedule():
    
    payload = request.get_json(silent=True) or {}
    
    body = ScheduleCreateRequest.model_validate(payload)

    db = get_db()

    try:
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
            row = cur.fetchone()
        db.commit()

    except pg_errors.ForeignKeyViolation as e:
        db.rollback()
        raise ConflictError(
            "foreign key violation: userId or statusTypeId does not exist"
        ) from e
    
    response_body = ScheduleResponse.model_validate(row).model_dump(
        mode="json", by_alias=True
    )

    headers = {"Location": url_for("schedules.create_schedule") + f"/{row['id']}"}
    
    return jsonify(response_body), 201, headers


@del_schedules_bp.post("/schedules/{id}")
def delete_schedule():
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute(
                "DELETE FROM schedules WHERE id = %{id}s RETURNING id"
            )
            row = cur.fetchone()
        db.commit()
         
    
    except pg_errors.NotFoundError as e:
        db.rollback()
        raise NotFoundError(
            "not found: userId is not found"
        )from e


    return ("", 204)

    
    