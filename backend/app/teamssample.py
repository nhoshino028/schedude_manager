from flask import Flask, jsonify, Blueprint
import psycopg
from psycopg.rows import dict_row #辞書型で返してくれるようインポート
from app import get_connection

app = Flask(__name__)

@app.route('/teamssample', methods=['GET'])
def get_teams():
    query = """ SELECT * FROM teams """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()

        result = []
        for row in rows:
            record = {
                "id": row['id'], "teamCode": row['team_code'],"name": row['name']
            }
            result.append(record)

        return jsonify(result)