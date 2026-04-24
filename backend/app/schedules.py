from flask import Blueprint, jsonify
from config import settings #関数のインポート
from psycopg.rows import dict_row #辞書型で返してくれるようインポート

schedule_app = Blueprint('/schedules', __name__, url_prefix='/schedules')

@schedule_app.route('/schedules')
def get_schedules():
    with spycopg.connect(settings.DATABASE_URL) as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT * FROM schedules")
            schedules = cur.fetchall()
            return jsonify(schedules)