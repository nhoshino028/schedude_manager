"""
model_answer バックエンドの設定を集約する pydantic-settings ベースのモジュール。

役割:
    環境変数や .env ファイルから設定値を読み込み、型付きで提供する。
    直接 os.environ を参照するのではなく、このモジュール経由で
    設定を取り出す（型付けと既定値の一元管理のため）。

インスタンス化方針:
    Flask の create_app() 内で 1 度だけ Settings() を生成し、
    app.config["SETTINGS"] に格納して共有する。
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    環境変数と .env から読み込む設定項目の定義クラス。

    属性:
        database_url (str):
            Phase1 以降で psycopg が使う PostgreSQL 接続文字列。
            形式: postgresql://<user>:<pass>@<host>:<port>/<db>
            Phase0 では未参照だが、Phase1 への足場として定義しておく。

        flask_debug (bool):
            Flask のデバッグモード有効/無効。True で自動リロードと
            詳細エラーページが有効になる。compose 側で 1 を渡す想定。

    暗黙的に利用するもの:
        - 環境変数名は大文字/小文字の両方を受け付ける（case_sensitive=False）。
        - .env ファイルがカレントディレクトリにあれば自動読込。
          ただし本プロジェクトでは compose の env_file 経由で注入するのが
          主経路なので、直接実行時のフォールバックとしての位置付け。
    """

    database_url: str = ""
    flask_debug: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
