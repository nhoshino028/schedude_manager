from flask import Blueprint, jsonify
from config import settings #関数のインポート
from psycopg.rows import dict_row #辞書型で返してくれるようインポート

work_status_types_app = Blueprint('work-status-types', __name__, url_prefix='/work-status-types')

@work_status_types_app.route('/work-status-types')
def get_types():
    with spycopg.connect(settings.DATABASE_URL) as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT * FROM work_status_types")
            work_status_types = cur.fetchall()
            return jsonify(work_status_types)