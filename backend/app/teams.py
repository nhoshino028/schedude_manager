from flask import Blueprint, jsonify
import spycopg
from psycopg.rows import dict_row #辞書型で返してくれるようインポート
from .config import settings #関数のインポート

teams_app = Blueprint('teams', __name__, url_prefix='/teams')

@teams_app.route('/')
def get_teams():
    with spycopg.connect(settings.DATABASE_URL) as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT * FROM teams")
            teams = cur.fetchall()
            return jsonify(teams)