from flask import Flask
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "My Flask App"

settings = Settings()

app = Flask(__name__)

@app.route('/')
def home():
    return f"Welcome to {settings.app_name}!"

if __name__ == "__main__":
    # host="0.0.0.0" がないとコンテナの外からアクセスできません
    app.run(debug=True, host="0.0.0.0", port=5000)