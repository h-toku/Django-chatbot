# ベースイメージ
FROM python:3.13-slim

# 作業ディレクトリを作成・設定
WORKDIR /app

# 必要なパッケージインストール（mariadb clientに変更）
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    pkg-config \
    libmariadb-dev \
    git \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# requirements.txt をコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# プロジェクトファイルをすべてコピー
COPY . .

# Djangoサーバー起動コマンド
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
