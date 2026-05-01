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
#from app.routes.reports import reports_bp

def create_app() -> Flask:
    app = Flask(__name__)


    settings = Settings()
    app.config["SETTINGS"] = settings
    app.json.sort_keys = False      #取得結果の順番がjsonify()のjson encoderでソートされないように設定
    app.json.ensure_ascii = False   #日本語の文字化けを解消
    app.debug = settings.flask_debug

    init_db(app)

    register_error_handlers(app)

    CORS(
        app,
        resources={
            r"/*": {
                "origins": [
                    "http://localhost:5173",
                    "http://localhost:8080",
                ]
            }
        },
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_header=["Content-Type"],
    )

    app.register_blueprint(health_bp)
    app.register_blueprint(work_status_types_bp)
    app.register_blueprint(schedules_bp)
    app.register_blueprint(teams_bp)
    app.register_blueprint(users_bp)
    #app.register_blueprint(reports_bp)

    return app
