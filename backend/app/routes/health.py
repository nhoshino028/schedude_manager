"""
model_answer バックエンドのヘルス/疎通確認用エンドポイントを提供する Blueprint。

役割:
    Phase0 の動作確認を成立させるための最小ハンドラ `GET /` を定義する。
    Phase1 以降で実装する業務エンドポイント（users / schedules / reports）
    とは独立しており、稼働確認・死活監視・受講者の最初の達成感の場として
    Phase 全体を通じて残す。

モジュール公開物:
    health_bp: Flask Blueprint。create_app() が register_blueprint で登録する。
"""

from flask import Blueprint, jsonify

# Blueprint 名は "health"。url_prefix は指定せずルート直下にマップする。
# 第二引数 __name__ は Blueprint が自身のテンプレート/静的ファイルを探す
# 起点モジュールとして必要（Phase0 では未使用だが Flask の要求仕様）。
health_bp = Blueprint("health", __name__)


@health_bp.get("/")
def get_root():
    """
    ルートパス GET / のヘルス応答ハンドラ。

    処理:
        固定 JSON {"status": "ok", "service": "model_answer_backend"} を
        200 OK で返す。DB 接続やファイル I/O など外部依存は一切参照しない。

    引数:
        なし。クエリパラメータ・リクエストボディは読み取らない。

    戻り値:
        flask.Response。
        Content-Type は application/json（flask.jsonify が自動付与）。
        JSON ボディ: {"status": "ok", "service": "model_answer_backend"}

    暗黙的に利用するもの:
        - flask.jsonify はレスポンスヘッダを application/json に自動設定する。
        - このハンドラは Flask が routing で自動的に呼び出す（ユーザーが
          直接呼ぶコードは書かない）。
    """
    return jsonify({"status": "ok", "service": "model_answer_backend"})
