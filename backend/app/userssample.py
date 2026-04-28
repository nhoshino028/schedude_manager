from flask import Flask, jsonify, Blueprint
import psycopg
from psycopg.rows import dict_row #辞書型で返してくれるようインポート
from app import get_connection

app = Flask(__name__)

@app.route('/userssample', methods=['GET'])
def get_users():
    query = """ SELECT * FROM users """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()

        result = []
        for row in rows:
            record = {
                "id": row['id'], "employeeCode": row['employee_code'] ,"name": row['name'], "team": row['team_id'], "createdAt": row['created_at']
            }
            result.append(record)

        return jsonify(result)