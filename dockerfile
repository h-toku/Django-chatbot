# ベースイメージ
FROM python:3.12

# 必要なシステムパッケージ（PostgreSQLクライアント）をインストール
RUN apt-get update && apt-get install -y \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリを作成
WORKDIR /code

# 依存ファイルをコピーしてインストール
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# プロジェクトコードをコピー
COPY . .

# コンテナ起動時に実行するコマンド（必要に応じて）
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
