from flask import Blueprint, jsonify
from config import settings #関数のインポート
from psycopg.rows import dict_row #辞書型で返してくれるようインポート

users_app = Blueprint('users', __name__, url_prefix='/users')

@users_app.route('/users')
def get_users():
    with spycopg.connect(settings.DATABASE_URL) as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT * FROM users")
            users = cur.fetchall()
            return jsonify(users)