from flask import Blueprint, jsonify, request

from app.db import get_db
from app.schemas.reports import MonthlyReport, YearMonthQuery

reports_bp = Blueprint("reports", __name__)

@reports_bp.get("/reports/monthly")
def list_reports():

    query = YearMonthQuery.model_validate(request.args.to_dict())

    db = get_db()
    with db.cursor() as cur:
        #sqlの内容
        sql = """
            SELECT
                json_build_object('id', u.id, 'name', u.name) AS user,
                m.year_month,
                m.office_days,
                m.remote_days,
                m.paid_leave_days,
                m.am_leave_count,
                m.pm_leave_count,
                m.absence_days,
                m.updated_at
            from monthly_schedule_summary m
            JOIN users u
                on m.user_id = u.id
            JOIN teams t
                on u.team_id = t.id
            WHERE m.year_month = %(year_month)s
            """
        
        #パラメータの内容指定
        params = {
            "year_month": query.year_month,
        }

        #teamIdの指定されている場合
        if query.team_id is not None:
            sql += """
                AND u.team_id = %(team_id)s
            """
            params["team_id"] = query.team_id

        sql += """
        ORDER BY u.id;
        """
        cur.execute(sql,params)
        rows = cur.fetchall()


    items = [
        MonthlyReport.model_validate(row).model_dump(mode="json", by_alias=True)
        for row in rows
    ]
    return jsonify(items), 200
