from flask import Blueprint, jsonify
from config import settings #関数のインポート
from psycopg.rows import dict_row #辞書型で返してくれるようインポート

delete_app = Blueprint('/schedules/{id}', __name__, url_prefix='/schedules/{id}')

@delete_app.route('/schedules/{id}', methods=['DELETE'])
def delete_schedule():
    with psycopg.connect(settings.DATABASE_URL) as conn:
        with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    "DELETE FROM schedules"
                    "WHERE user_id = '2';"
                )
        return f"削除が成功しました。"