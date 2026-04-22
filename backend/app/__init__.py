#pythonパッケージの初期化を行うときに利用される

import json
from flask import Flask, jsonify
import psycopg
from psycopg.rows import dict_row
from pydantic_settings import BaseSettings
from dotenv import load_dotenv


class Settings(BaseSettings):
    app_name: str = "My Flask App"
    database_url: str
    DEBUG: bool = False
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
#.envファイルを見に行く
settings = Settings()

#flaskアプリを初期化
app = Flask(__name__)

# blueprintの登録
# 機能一つ一つをBluepointとする
# 機能ごとに作成したbluepointを__init__.pyに登録してアプリに組み込む）

# app.register_bluepoint() メソッドを使う

@app.route('/')
def home():
    return f"Welcome to {Settings.app_name}!"

#teamsテーブルの取得
@app.route('/teams', methods=['GET'])
def get_teams():
    with psycopg.connect(settings.database_url) as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT * FROM teams")
    teams = cur.fetchall()

    return jsonify(teams)


#usersテーブルの取得  クエリの部分とネストで返す部分がよく分かんないのでとりあえず基本形として作成
@app.route('/users', methods=['GET'])
def get_users():
    with psycopg.connect(settings.database_url) as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT * FROM users")
    users = cur.fetchall()

    return jsonify(users)
    

#work-status-typesテーブルの取得
@app.route('/work-status-types', methods=['GET'])
def get_types():
    with psycopg.connect(settings.database_url) as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT * FROM work-status-types")
    work_status_types = cur.fetchall()

    return jsonify(work_status_types)


#schedulesテーブルの取得、データの登録
@app.route('/schedules', methods=['GET', 'POST', 'PUT', 'DELETE'])
def schedules():
    #取得
    if request.method == 'GET':
        with psycopg.connect(settings.database_url) as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("SELECT * FROM schedules")
        return jsonify(cur.fetchall())

    #登録
    else request.method == 'POST':
        with psycopg.connect(settings.database_url) as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    "INSERT INTO schedules (id, user_id, target_date, status_type_id, start_time, end_time, comment, created_at, updated_at) "
                    "VALUES"
                    "('5', '006', '2026-04-16', '06', null, null, '体調不良', '2026-04-16 08:30:00', '2026-04-16 08:30:00');"
                )
    
#schedulesテーブルの更新、削除
@app.route('/schedules/{id}', methods=['PUT', 'DELETE'])
    #更新(ちょっと悩む)
def edit_schedules():
    if request.method == 'PUT':
        with psycopg.connect(settings.database_url) as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    "UPDATE monthly_schedule_summary SET absence_days = absence_days +1"
                    "WHERE user_id = 5;"
                )
    
    #削除
    else request.method == 'DELETE':
         with psycopg.connect(settings.database_url) as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    "DELETE FROM schedules"
                    "WHERE user_id = '2';"
                )




if __name__ == "__main__":
    # host="0.0.0.0" がないとコンテナの外からアクセスできません
    app.run(host='0.0.0.0', debug=True, port=8000)
