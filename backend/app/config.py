from pydantic_settings import BaseSettings, SettingsConfigDict

#接続設定
class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@postgres:5432/schedule_manager"
    DEBUG: bool = False
    model_config = SettingsConfigDict(extra="ignore")
    
#settingのインスタンス化
settings = Settings()