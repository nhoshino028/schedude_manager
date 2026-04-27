"""
model_answer バックエンドの DB 接続ライフサイクル管理モジュール。

役割:
    psycopg 3.x を用いた PostgreSQL 接続を、Flask のリクエスト毎に
    生成・後始末するための薄いヘルパー群を提供する。コネクションプールは
    導入せず、リクエスト 1 回につき 1 接続を作って閉じる素朴な実装。
    教育目的で「接続のライフサイクル」を明確に見せるための設計。

公開物:
    get_db() -> psycopg.Connection
        現リクエスト用の接続を返す。Flask の g に保存される。
    close_db(exc=None) -> None
        現リクエスト用の接続を閉じる。Flask の teardown_appcontext から
        自動で呼ばれる前提。
    init_app(app) -> None
        Flask アプリケーションに close_db を登録する 1 行ヘルパー。
        create_app() 内で呼ぶ。

呼び出し関係:
    - 上流: app/__init__.py の create_app() が init_app(app) を呼ぶ。
    - 下流: app/routes/*.py のハンドラ関数が get_db() を呼び出して接続を取得。
"""

import psycopg
from psycopg.rows import dict_row
from flask import Flask, g, current_app


def get_db() -> psycopg.Connection:
    """
    現在の Flask リクエストに紐づく psycopg 接続を返す。

    処理:
        1. Flask の g オブジェクトに db 属性が無ければ、
           current_app.config["SETTINGS"].database_url を読み取り、
           psycopg.connect() で新規接続を作る。
        2. 接続には row_factory=dict_row を指定し、SELECT 結果が
           {"column_name": value, ...} の dict として返るようにする。
        3. autocommit は明示的に False を指定する（psycopg 3 既定値だが
           「教育目的で明示する」意図でコメントとともに残す）。
        4. 生成した接続を g.db に保存して返却。
        5. 既に g.db があればそれを返すだけ。

    引数:
        なし。Flask のリクエストコンテキスト内で呼ぶこと。

    戻り値:
        psycopg.Connection: 現リクエスト用の DB 接続。

    暗黙的に利用するもの:
        - flask.current_app.config["SETTINGS"].database_url: 接続文字列の出所。
          create_app() で Settings インスタンスが格納されている前提。
        - flask.g: リクエストスコープのストレージ。Flask が自動管理。
    """
    if "db" not in g:
        settings = current_app.config["SETTINGS"]
        g.db = psycopg.connect(
            settings.database_url,
            row_factory=dict_row,
            autocommit=False,  # psycopg 3 の既定値だが、明示することでお手本コードでの commit() の意義を強調する
        )
    return g.db


def close_db(exc: BaseException | None = None) -> None:
    """
    現在の Flask リクエストに紐づく psycopg 接続を閉じる。

    処理:
        1. g.pop("db", None) で接続を取り出す（無ければ None）。
        2. 接続が存在すれば close() を呼ぶ。
        3. 接続が無ければ何もしない（ハンドラ内で get_db() を呼ばなかった
           ケース、たとえばヘルスチェックのような DB 不要のリクエスト）。

    引数:
        exc: BaseException | None
            Flask の teardown_appcontext が渡す引数。リクエスト中に発生した
            例外（あれば）。本関数は使用しないが、Flask 側のシグネチャに
            合わせて受け取る。

    戻り値:
        None。

    暗黙的に利用するもの:
        - flask.g: 接続の取り出し元。
        - psycopg.Connection.close(): エラー時もリソースを確実に解放するため
          呼び出す。close() 自体は冪等で再呼出しても問題ない。
    """
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_app(app: Flask) -> None:
    """
    Flask アプリケーションに close_db を teardown_appcontext として登録する。

    処理:
        app.teardown_appcontext(close_db) を呼ぶだけの 1 行ヘルパー。
        この登録により、リクエスト終了時 (またはアプリコンテキスト pop 時)
        に close_db が自動で呼ばれ、接続が確実に閉じられる。

    引数:
        app: flask.Flask
            create_app() 内で生成された Flask インスタンス。

    戻り値:
        None。

    暗黙的に利用するもの:
        - close_db 関数本体。
        - Flask の teardown_appcontext シグナル機構。
    """
    app.teardown_appcontext(close_db)
