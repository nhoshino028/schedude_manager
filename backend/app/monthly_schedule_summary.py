from flask import Blueprint, jsonify
from config import settings #関数のインポート
from psycopg.rows import dict_row #辞書型で返してくれるようインポート

monthly_schedule_summary_app = Blueprint('/reports/monthly', __name__, url_prefix='/reports/monthly')

@monthly_schedule_summary_app.route('/reports/monthly')
def get_monthly():
    with spycopg.connect(settings.DATABASE_URL) as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT * FROM monthly_schedule_summary")
            monthly_schedule_summary = cur.fetchall()
            return jsonify(monthly_schedule_summary)