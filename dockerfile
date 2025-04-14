# ベースイメージ
FROM python:3.9

# 作業ディレクトリを作成・設定
WORKDIR /app

# 必要なパッケージインストール（mysqlclient などに必要）
RUN apt-get update && \
    apt-get install -y gcc default-libmysqlclient-dev && \
    apt-get clean

# requirements.txt をコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir --no-deps -r requirements.txt

# プロジェクトファイルをすべてコピー
COPY . .

# Djangoサーバー起動コマンド
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
