import psycopg
from psycopg.rows import dict_row
from flask import Flask, g, current_app

# 現在のFlaskリクエストに基づくpsycopgの接続を返す
def get_db() -> psycopg.Connection:
    if "db" not in g:
        #gオブジェクトにdb属性が入っていないとき、database_urlを読み取って新規接続を作る
        settings = current_app_config["SETTINGS"]
        g.db = psycopg.connect(
            settings.database_url,
            row_factory=dict_row,
            autocommit=False,  # psycopg 3 の既定値だが、明示することでお手本コードでの commit() の意義を強調する
        )
    return g.db  #作成した接続をg.dbに保存してreturnまたはg.dbがある場合はそのまま返すだけ

