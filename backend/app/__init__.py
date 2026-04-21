#pythonパッケージの初期化を行うときに利用される

from flask import Flask, jsonify, request
from database import pool
from psycopg.rows import dict_row

class Settings(BaseSettings):
    app_name: str = "My Flask App"

settings = Settings()

app = Flask(__name__)

# blueprintの登録
# 機能一つ一つをBluepointとする
# 機能ごとに作成したbluepointを__init__.pyに登録してアプリに組み込む）

# app.register_bluepoint() メソッドを使う

@app.route('/')
def home():
    return f"Welcome to {settings.app_name}!"


@app.route('/teams', methods=['GET'])
def get_teams():



if __name__ == "__main__":
    # host="0.0.0.0" がないとコンテナの外からアクセスできません
    app.run(host='0.0.0.0', debug=True, port=8000)
