from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException
from pydantic import ValidationError

class APIError(Exception):
    #サブクラスに対してクラス属性を共通化して書きやすく管理しやすくする
    code: str = "API_ERROR"    #エラーレスポンスの"code"フィールドに入る文字列
    message: str = "api error"    #エラーメッセージ　インスタンス化時に上書きができる
    status_code = int = 500    #HTTPステータスコード

    #カスタムメッセージ付きで例外を初期化
    #コンテキスト固有のメッセージで上書きしたいときに返して、Noneの場合はクラス属性messageをそのまま使う
    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.message)
        if message is not None:
            self.message = message

class NotFoundError(APIError):
    #指定されたリソースが見つからない場合にraiseする例外
    code = "NOT_FOUND"
    status_code = 404
    message = "resource not found"

class ConflictError(APIError):
    #一意制約や外部キー制約に違反したときにraiseする例外
    code = "CONFLICT"
    status_code = 409
    message = "conflict"

class QueryValidationError(Exception):
    pass

def register_error_handlers(app: Flask) -> None:

    @app.errorhandler(ValidationError)
    #pydanticのerrors()をdetails 形式に変換する
    def _on_validation_error(e: ValidationError):
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
    
    @app.errorhandler(QueryValidationError)
    def _on_query_validation_error(e:QueryValidationError):
        return jsonify({
            "code": "VALIDATION_ERROR",
            "message": str(e),
        }),400

    @app.errorhandler(APIError)
    def _on_api_error(e: APIError):
    # NotFoundError/ConflictErrorなどのサブクラスもこのハンドラで捕捉する
        return jsonify({
            "code": e.code,
            "message": e.message,
            "details": None,
        }), e.status_code
    
    @app.errorhandler(HTTPException)
    def _on_http_exception(e: HTTPException):
    # ルート未定義（404）やMethod not Allowed（405）などのFlask/werkzeugが自動でraizeするHTTPExceptionを統一形式に変換
        return jsonify({
            "code": "HTTP_ERROR",
            "message": e.description,
            "details": None,
        }), (e.code or 500)
    
    @app.errorhandler(Exception)
    def _on_unexpected(e: Exception):
        #上記3つに該当しない例外(psycopgのOperationalError等)はここで変換する
        #stacktraceはapp.loger.exception()で出力し、外部にはサニタイズしたメッセージのみ返す
        app.logger.exception("Unexpected error: %s", e)
        return jsonify({
            "code": "INTERNAL_ERROR",
            "message": "internal server error",
            "details": None,
        }), 500
