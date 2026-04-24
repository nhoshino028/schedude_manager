#pythonパッケージの初期化を行うときに利用される

from flask import Flask, jsonify, Blueprint
import psycopg
from pydantic_settings import BaseSettings, SettingsConfigDict

#flaskアプリを初期化
app = Flask(__name__)


#日本語を文字化けしないようにする
app.json.ensure_ascii = False

@app.route('/')
def home():
    return f"おはようございます。勤務予定管理TOPです。"



if __name__ == "__main__":
    # host="0.0.0.0" がないとコンテナの外からアクセスできません
    app.run(host='0.0.0.0', debug=True, port=8000)
