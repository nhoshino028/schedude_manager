# ============================================================
# model_answer バックエンドイメージ
#
# 方針（CLAUDE.md）:
#   - 本番起動 (docker compose up) にも DevContainer にも
#     同じイメージを使う（単一 Dockerfile 再利用）
#
# ベース: python:3.12-slim
#   - 開発ルール・ガイド.md で Python 3.12 を指定
#   - slim バリアントは Debian 系ベースで最小限、サイズ約 150MB
# ============================================================

FROM python:3.12-slim

# OS パッケージ追加:
#   - git: DevContainer の Source Control ビュー動作に必要
#   - curl: ヘルスチェック手動確認用。学習中の疎通確認に便利
#   - build-essential: psycopg[binary] はビルド済みホイールだが、
#     将来何かビルドが必要なパッケージが入った際の保険
# --no-install-recommends で余計な推奨パッケージを避け、
# /var/lib/apt/lists/* を削除してイメージサイズを節約する。
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git \
        curl \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# コンテナ内作業ディレクトリ。compose のバインドマウント先でもある。
WORKDIR /app

# 依存定義を先にコピーすることで、コード変更時に依存再インストールを
# 走らせずに済む（Docker レイヤキャッシュの効かせ方）。
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリ本体は compose のバインドマウント (./backend:/app) で上書きされるが、
# compose を介さず単独でイメージ実行する場合に備えてここでもコピーする。
COPY . .

# Flask 開発サーバの待ち受けポート。compose の ports 指定と合わせる。
EXPOSE 8000

# CMD は compose 側で --debug 付きに上書きする想定。
# 単独で docker run する場合のフォールバックとして最低限のコマンドを指定。
CMD ["flask", "--app", "app:create_app", "run", "--host", "0.0.0.0", "--port", "8000"]
