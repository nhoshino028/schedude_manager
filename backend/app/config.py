# 環境変数や.envファイルから設定値を読み込み、型付きで提供する

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = ""
    flask_debug: bool = False

    # 直接実行時のフォールバックとして設置
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )