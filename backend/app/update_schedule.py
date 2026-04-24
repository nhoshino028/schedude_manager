from flask import Blueprint
from config import settings #関数のインポート
from psycopg.rows import dict_row #辞書型で返してくれるようインポート

update_app = Blueprint('/schedules/{id}', __name__, url_prefix='/schedules/{id}')

@update_app.route('/schedules/{id}', methods=['PUT'])
def update_schedule():
    with spycopg.connect(settings.DATABASE_URL) as conn:
        with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    "UPDATE monthly_schedule_summary SET absence_days = absence_days +1"
                    "WHERE user_id = 5;"
                )
        return f"更新が成功しました。"