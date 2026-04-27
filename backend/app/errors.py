"""
model_answer バックエンドの共通エラーハンドラとカスタム例外を集約するモジュール。

役割:
    API 仕様書 §1 で定義された共通エラーレスポンス形式
    {"code": str, "message": str, "details": list | None}
    に全エラーを統一して変換するための Flask errorhandler 群と、
    routes 側から raise するためのカスタム例外クラスを提供する。

公開物:
    APIError: カスタム API エラーの基底クラス（直接 raise はしない想定）
    NotFoundError: 404 を返すための例外（code=NOT_FOUND）
    ConflictError: 409 を返すための例外（code=CONFLICT）
    register_error_handlers(app): Flask に 4 種類の errorhandler を登録

呼び出し関係:
    - 上流: app/__init__.py の create_app() が register_error_handlers(app)
      を呼ぶ。
    - 下流: app/routes/schedules.py のお手本実装が ConflictError を raise
      する。受講者は雛形ファイル内のヒントに従い NotFoundError も使う想定。
    - 暗黙呼び出し: pydantic.ValidationError は routes が raise しなくても
      pydantic.model_validate(...) で自動 raise されるので、本ハンドラで
      キャッチして 400 にマップする。
"""

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException
from pydantic import ValidationError


class APIError(Exception):
    """
    本プロジェクトのカスタム API エラーの基底クラス。

    役割:
        サブクラス (NotFoundError / ConflictError) に対して
        code / status_code / message のクラス属性を共通化する。

    クラス属性:
        code (str): エラーレスポンス JSON の "code" フィールドに入る文字列。
        message (str): デフォルトのエラーメッセージ。インスタンス化時に
                       上書きできる。
        status_code (int): HTTP ステータスコード。

    暗黙的に利用するもの:
        Python の Exception 基底クラスの仕組み。raise するだけで
        register_error_handlers が登録した errorhandler が捕捉する。
    """
    code: str = "API_ERROR"
    message: str = "api error"
    status_code: int = 500

    def __init__(self, message: str | None = None) -> None:
        """
        カスタムメッセージ付きで例外を初期化する。

        引数:
            message: str | None
                コンテキスト固有のメッセージで上書きしたいときに渡す。
                None の場合はクラス属性 message をそのまま使う。

        戻り値: なし

        暗黙的に利用するもの: なし
        """
        super().__init__(message or self.message)
        if message is not None:
            self.message = message


class NotFoundError(APIError):
    """
    指定されたリソースが見つからない場合に raise する例外。

    code: "NOT_FOUND"
    status_code: 404
    用途例: PUT /schedules/{id} で id が存在しないとき (受講者課題内で利用)
    """
    code = "NOT_FOUND"
    status_code = 404
    message = "resource not found"


class ConflictError(APIError):
    """
    一意制約や外部キー制約に違反したときに raise する例外。

    code: "CONFLICT"
    status_code: 409
    用途例: お手本 POST /schedules で psycopg.errors.ForeignKeyViolation を
    捕捉したとき。
    """
    code = "CONFLICT"
    status_code = 409
    message = "conflict"


def register_error_handlers(app: Flask) -> None:
    """
    Flask アプリに API 仕様書 §1 準拠のエラーハンドラを 4 種類登録する。

    処理:
        以下 4 つの errorhandler を app に紐付ける。
        1. ValidationError (pydantic): 400 VALIDATION_ERROR + details
        2. APIError (本モジュール定義): code / status_code を流用
        3. HTTPException (werkzeug): 404 など Flask 既定エラーを統一形式に
        4. Exception (最終受け): 想定外を 500 INTERNAL_ERROR にする

    引数:
        app: flask.Flask
            create_app() 内で生成された Flask インスタンス。

    戻り値:
        None。

    暗黙的に利用するもの:
        - Flask の errorhandler デコレータ機構。
        - app.logger: 想定外エラーは exception() で stacktrace ごとログ出力。
        - flask.jsonify: レスポンス JSON のシリアライズと Content-Type 自動付与。
    """

    @app.errorhandler(ValidationError)
    def _on_validation_error(e: ValidationError):
        # pydantic の errors() は [{loc, msg, type, input, url, ...}] のリスト。
        # 仕様書 §1 の details 形式 [{field, reason}] に変換する。
        # loc は ("body", "userId") のようなタプル。"." 区切りでフィールド名にする。
        details = [
            {
                "field": ".".join(str(p) for p in err["loc"]),
                "reason": err["msg"],
            }
            for err in e.errors()
        ]
        return jsonify({
            "code": "VALIDATION_ERROR",
            "message": "request validation failed",
            "details": details,
        }), 400

    @app.errorhandler(APIError)
    def _on_api_error(e: APIError):
        # NotFoundError / ConflictError などのサブクラスもこのハンドラで捕捉する。
        # status_code と code はクラス属性、message はインスタンス属性 (上書き可)。
        return jsonify({
            "code": e.code,
            "message": e.message,
            "details": None,
        }), e.status_code

    @app.errorhandler(HTTPException)
    def _on_http_exception(e: HTTPException):
        # ルート未定義 (404) や Method Not Allowed (405) など、
        # Flask / werkzeug が自動で raise する HTTPException を統一形式に変換。
        # e.code は HTTP ステータス、e.description はデフォルトメッセージ。
        # HTTPException 抽象基底 そのものは code=None なので、防御的に 500 にフォールバック
        # する。実用上 ここに到達するのは具象サブクラス (404 / 405 等) なので fallback が
        # 効くケースは稀だが、教育目的でも「型が None になり得るときはガードする」の見本になる。
        return jsonify({
            "code": "HTTP_ERROR",
            "message": e.description,
            "details": None,
        }), (e.code or 500)

    @app.errorhandler(Exception)
    def _on_unexpected(e: Exception):
        # 上記 3 つに該当しない例外 (psycopg の OperationalError 等) は
        # ここで最終受けする。stacktrace は app.logger.exception() で
        # 出力し、外部にはサニタイズしたメッセージのみ返す。
        app.logger.exception("Unexpected error: %s", e)
        return jsonify({
            "code": "INTERNAL_ERROR",
            "message": "internal server error",
            "details": None,
        }), 500
