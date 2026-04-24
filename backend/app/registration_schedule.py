from flask import Blueprint
from config import settings #関数のインポート
from psycopg.rows import dict_row #辞書型で返してくれるようインポート

registration_app = Blueprint('/schedules', __name__, url_prefix='/schedules')

@registration_app.route('shedules', methods=['POST'])
def register_schedule():
    with spycopg.connect(settings.DATABASE_URL) as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                    "INSERT INTO schedules (id, user_id, target_date, status_type_id, start_time, end_time, comment, created_at, updated_at) "
                    "VALUES"
                    "('5', '006', '2026-04-16', '06', null, null, '体調不良', '2026-04-16 08:30:00', '2026-04-16 08:30:00');"
            )
            return f"登録が成功しました。"