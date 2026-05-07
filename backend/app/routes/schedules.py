from flask import Blueprint, jsonify, request, url_for
from psycopg import errors as pg_errors

from app.db import get_db
from app.errors import ConflictError
from app.errors import NotFoundError
from app.schemas.schedules import ScheduleCreateRequest, ScheduleUpdateRequest, ScheduleResponse

schedules_bp = Blueprint("schedules", __name__)

# 登録
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


# 更新
@schedules_bp.put("/schedules/<int:id>")
def put_schedule(id):

    payload = request.get_json(silent=True)
    body = ScheduleUpdateRequest.model_validate(payload)
    db = get_db()

    try:
        with db.cursor() as cur:
            cur.execute(
                """
                    UPDATE schedules
                    SET
                        user_id = %(user_id)s,
                        target_date = %(target_date)s,
                        status_type_id = %(status_type_id)s,
                        start_time = %(start_time)s,
                        end_time = %(end_time)s,
                        comment = %(comment)s,
                        updated_at = now()
                    WHERE id = %(id)s 
                    RETURNING *
                """,
                # WHERE id = %(id)sを認識してもらうために入れる
                {**body.model_dump(),
                 "id": id,
                }
            )
            row = cur.fetchone()

            #存在しない場合にNotFoundErrorを返す
            if row is None:
                raise NotFoundError("not found: Schedule not found")
        db.commit()

    except NotFoundError:
        db.rollback()
        raise
    
    response_body = ScheduleResponse.model_validate(row).model_dump(
        mode="json", by_alias=True
    )
    
    return jsonify(response_body), 200


# 削除
@schedules_bp.delete("/schedules/<int:id>")
def delete_schedule(id):
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute(
                "DELETE FROM schedules WHERE id = %(id)s RETURNING id"
            ),
            {
                "id": id,
            }
            row = cur.fetchone()

            if row is None:
                raise NotFoundError("not found: Schedule not found")
        db.commit()
         
    except NotFoundError:
        db.rollback()
        raise

    return ("", 204)

    
    