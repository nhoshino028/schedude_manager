FROM python:3.12-slim

# OSパッケージの追加
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# flask起動コマンド

CMD ["flask", "--app", "app:create_app", "run", "--host", "0.0.0.0", "--port", "8000"]