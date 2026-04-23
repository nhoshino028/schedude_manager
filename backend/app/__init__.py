#pythonパッケージの初期化を行うときに利用される

import json
from flask import Flask, jsonify, request
import psycopg
from psycopg.rows import dict_row
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
from datetime import date, time


class Settings(BaseSettings):
    DATABASE_URL: str
    DEBUG: bool = False
    model_config = SettingsConfigDict(extra="ignore")
    
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
    return f"おはようございます。勤務予定管理TOPです。"

#teamsテーブルの取得
@app.route('/teams', methods=['GET'])
def get_teams():
    with psycopg.connect(settings.DATABASE_URL) as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT * FROM teams")
            teams = cur.fetchall()

    return jsonify(teams)


#usersテーブルの取得  クエリの部分とネストで返す部分がよく分かんないのでとりあえず基本形として作成
@app.route('/users', methods=['GET'])
def get_users():
    with psycopg.connect(settings.DATABASE_URL) as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT * FROM users")
            users = cur.fetchall()

    return jsonify(users)
    

#work-status-typesテーブルの取得
@app.route('/work-status-types', methods=['GET'])
def get_types():
    with psycopg.connect(settings.DATABASE_URL) as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT * FROM work_status_types")
            work_status_types = cur.fetchall()

    return jsonify(work_status_types)


#schedulesテーブルの取得、データの登録
@app.route('/schedules', methods=['GET', 'POST'])
def schedules():
    #取得
    if request.method == 'GET':
        with psycopg.connect(settings.DATABASE_URL) as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("SELECT * FROM schedules")
                schedules = cur.fetchall()
            #DATE型とTIME型を文字列に変換する
            format_schedules = [{
                "target_date": row["target_date"].isoformat(),
                "start_time": row["start_time"].strftime("%H:%M")
            }
            for row in schedules
            ]
            return jsonify(format_schedules)

    #登録
    elif request.method == 'POST':
        with psycopg.connect(settings.DATABASE_URL) as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    "INSERT INTO schedules (id, user_id, target_date, status_type_id, start_time, end_time, comment, created_at, updated_at) "
                    "VALUES"
                    "('5', '006', '2026-04-16', '06', null, null, '体調不良', '2026-04-16 08:30:00', '2026-04-16 08:30:00');"
                )
        return f"登録が成功しました。"
    
#schedulesテーブルの更新、削除
@app.route('/schedules/{id}', methods=['PUT', 'DELETE'])
    #更新
def edit_schedules():
    if request.methods == 'PUT':
        with psycopg.connect(settings.DATABASE_URL) as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    "UPDATE monthly_schedule_summary SET absence_days = absence_days +1"
                    "WHERE user_id = 5;"
                )
        return f"更新が成功しました。"
    
    #削除
    elif request.method == 'DELETE':
         with psycopg.connect(settings.DATABASE_URL) as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    "DELETE FROM schedules"
                    "WHERE user_id = '2';"
                )
         return f"削除が成功しました。"

@app.route('/reports/monthly', methods=['GET'])
def get_monthly():
    with psycopg.connect(settings.DATABASE_URL) as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute("SELECT * FROM monthly_schedule_summary")
            monthly_schedule_summary = cur.fetchall()

    return jsonify(monthly_schedule_summary)

#エラーハンドリング
#returnは仮で文字を返すようにしています。DB定義書のようにdetailsを表示する方法を考え中（データからどうやってエラーとなったカラムをdetailsに反映させるのか）
#400エラー
@app.errorhandler(400)
def validationErr(error):
    return f"Validation Error", 400

#404エラー
@app.errorhandler(404)
def notFoundErr(error):
    return f"Data not found", 404

#409エラー
@app.errorhandler(409)
def conflictError(error):
    return f"Conflict Error", 409

#500エラー
@app.errorhandler(500)
def internalErr(error):
    return f"Internal Error", 500



if __name__ == "__main__":
    # host="0.0.0.0" がないとコンテナの外からアクセスできません
    app.run(host='0.0.0.0', debug=True, port=8000)
