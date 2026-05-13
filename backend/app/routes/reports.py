from flask import Blueprint

from app.db import get_db
from app.schemas.reports import MonthlyReport

reports_bp = Blueprint("reports", __name__)

@reports_bp.get("/reports/monthly")
def list_reports():
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """
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
            on 
            """
        )
