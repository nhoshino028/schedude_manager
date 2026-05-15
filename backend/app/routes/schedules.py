from flask import Blueprint, jsonify, request, url_for
from psycopg import errors as pg_errors

from app.db import get_db
from app.errors import ConflictError
from app.errors import NotFoundError, ValidationError
from app.schemas.schedules import Schedule, ScheduleQuery, ScheduleCreateRequest, ScheduleUpdateRequest, ScheduleResponse

schedules_bp = Blueprint("schedules", __name__)

# 取得
@schedules_bp.get("/schedules")
def list_schedule():
    #schemaでモデルを作る
    query = ScheduleQuery.model_validate(request.args.to_dict())



    #where句の動的組み立て
    conditions = []
    params = {}

    if query.target_date:
        conditions.append("target_date = %(target_date)s")
        params["target_date"] = query.target_date

    if query.user_id:
        conditions.append("user_id = %(user_id)s")
        params["user_id"] = query.user_id

    if query.start_time:
        conditions.append("start_time >= %(start_time)s")
        params["start_time"] = query.start_time

    if query.end_time:
        conditions.append("end_time <= %(end_time)s")
        params["end_time"] = query.end_time

    where_clause = ""

    if conditions:
        where_clause = " WHERE " + " AND ".join(conditions)
    
    #型の確認
    #print(query.start_time)
    #print(type(query.start_time))

    #print(query.end_time)
    #print(type(query.end_time))

    #print(params)
    #print(where_clause)

    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute(
                f"""
                    SELECT
                        s.id, 
                        json_build_object('id', u.id, 'name', u.name) AS user, 
                        s.target_date, 
                        json_build_object('id', w.id, 'statusCode', w.status_code, 'statusName', w.status_name) AS status_type,
                        s.start_time,  
                        s.end_time, 
                        s.comment, 
                        s.created_at, 
                        s.updated_at
                    FROM schedules s
                    JOIN users u
                        on s.user_id = u.id
                    JOIN work_status_types w
                        on s.status_type_id = w.id
                        {where_clause}
                        ORDER BY s.id;      
                """,
                params,
            )
            rows = cur.fetchall()

    except ValueError:
        db.rollback()
        
    items = [
        Schedule.model_validate(row).model_dump(mode="json", by_alias=True)
        for row in rows
    ]

    return jsonify(items), 200


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
                "DELETE FROM schedules WHERE id = %(id)s RETURNING id",
            {
                "id": id,
            }
            )
            row = cur.fetchone()

            if row is None:
                raise NotFoundError("not found: Schedule not found")
        db.commit()
         
    except NotFoundError:
        db.rollback()
        raise

    return ("", 204)

    
    