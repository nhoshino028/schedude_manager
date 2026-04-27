"""
model_answer バックエンドアプリケーションの生成を司るモジュール。

役割:
    Flask インスタンスを生成する `create_app()` 関数 (Application Factory)
    を提供する。本ファイル自体はルーティングを持たず、設定の読み込み・
    エラーハンドラ登録・DB ライフサイクル登録・CORS 設定・Blueprint 登録
    のみを行う。

create_app() の呼び出し元:
    - `flask --app "app:create_app"` コマンド (compose の command で指定)
    - 将来のテスト・スクリプト用途 (本プロジェクトでは未使用)

Application Factory パターンを採用する理由:
    - 設定と Flask インスタンスの生成を分離することで、環境ごとの差し替え
      (dev/test/prod) が容易になる。
    - Phase2 で複数の Blueprint を登録するため、登録場所を集約する。
"""

from flask import Flask
from flask_cors import CORS

from app.config import Settings
from app.db import init_app as init_db
from app.errors import register_error_handlers
from app.routes.health import health_bp
from app.routes.work_status_types import work_status_types_bp
from app.routes.schedules import schedules_bp
from app.routes.teams import teams_bp
from app.routes.users import users_bp
from app.routes.reports import reports_bp


def create_app() -> Flask:
    """
    Flask アプリケーションインスタンスを生成して返す。

    処理:
        1. Flask インスタンス生成 (インポート名は __name__)。
        2. pydantic-settings で環境変数 / .env から Settings を読み込み、
           app.config["SETTINGS"] に格納し、flask_debug を app.debug に反映。
        3. app/db.init_app(app) を呼んで teardown_appcontext に close_db
           を登録する (リクエスト終了時に DB 接続を閉じる)。
        4. app/errors.register_error_handlers(app) を呼んで pydantic
           ValidationError / APIError / HTTPException / Exception の
           4 種類のハンドラを登録する。
        5. flask_cors.CORS で別オリジン (Phase3 のフロント /
           Phase0 のモック) からの呼び出しを許可。
        6. 全 Blueprint を register_blueprint で登録する。
           (お手本 2 + 雛形 4 + health の計 6 本)
        7. 完成した Flask インスタンスを返却。

    引数:
        なし。

    戻り値:
        flask.Flask: 設定 / ハンドラ / Blueprint が紐付けられた Flask アプリ。

    暗黙的に利用するもの:
        - 環境変数 FLASK_DEBUG / DATABASE_URL (Settings クラスが読み取る)
        - Flask は __name__ を起点にテンプレート/静的ファイルを探す
    """
    app = Flask(__name__)

    # 1. 設定オブジェクト読み込み。これ以後 app.config["SETTINGS"] で
    #    どこからでも参照できる。flask_debug は Flask の自動リロードに使う。
    settings = Settings()
    app.config["SETTINGS"] = settings
    app.debug = settings.flask_debug

    # 2. DB ライフサイクル登録。get_db() / close_db() の挙動は app/db.py 参照。
    #    teardown_appcontext を使うことで、リクエストエラー時もコネクションを
    #    確実に閉じる。
    init_db(app)

    # 3. 共通エラーハンドラ登録。pydantic.ValidationError / APIError 系 /
    #    werkzeug.HTTPException / 想定外の Exception を仕様書 §1 形式の
    #    JSON に変換する。詳細は app/errors.py 参照。
    register_error_handlers(app)

    # 4. CORS 設定。Phase3 のフロント (http://localhost:5173) と
    #    Phase0 モック (http://localhost:8080) から本 API を呼べるようにする。
    #    リクエストヘッダは Content-Type のみ許可 (認証ヘッダは Phase2 範囲外)。
    #    クレデンシャル (Cookie 等) は不要なので supports_credentials=False (既定)。
    CORS(
        app,
        resources={
            r"/*": {
                "origins": [
                    "http://localhost:5173",  # Phase3 のフロントエンド (Vite dev server)
                    "http://localhost:8080",  # Phase0 のモック HTML (docker-compose.mock.yml)
                ]
            }
        },
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type"],
    )

    # 5. Blueprint 登録。
    #    お手本完全実装: work_status_types_bp / schedules_bp の POST
    #    雛形 (ハンドラなし): teams_bp / users_bp / reports_bp /
    #                          schedules_bp の GET/PUT/DELETE
    #    既存: health_bp (Phase0 から動作する疎通確認)
    app.register_blueprint(health_bp)
    app.register_blueprint(work_status_types_bp)
    app.register_blueprint(schedules_bp)
    app.register_blueprint(teams_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(reports_bp)

    return app
