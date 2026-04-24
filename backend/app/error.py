from flask import Flask, Blueprint, jsonify
from config import settings #関数のインポート
from psycopg.rows import dict_row #辞書型で返してくれるようインポート

#flaskアプリを初期化
app = Flask(__name__)

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

