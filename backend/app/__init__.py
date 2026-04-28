#pythonパッケージの初期化を行うときに利用される

from flask import Flask, jsonify
import psycopg
from psycopg.rows import dict_row #辞書型で返してくれるようインポート
from pydantic_settings import BaseSettings, SettingsConfigDict


app = Flask(__name__)


def get_connection():
    return psycopg.connect(
        "host=postgres dbname=schedule_manager user=postgres password=postgres",
        row_factory=dict_row
    )
     
#日本語を文字化けしないようにする
app.json.ensure_ascii = False

@app.route('/')
def home():
    return f"おはようございます。勤務予定管理TOPです。"

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
    

if __name__ == "__main__":
    # host="0.0.0.0" がないとコンテナの外からアクセスできません
    app.run(host='0.0.0.0', debug=True, port=8000)
