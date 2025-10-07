# CircuitCraft AI - バックエンド

## プロジェクト概要

このディレクトリには、Circuit Craft AIアプリケーションのバックエンドAPIが含まれています。
FastAPIとSQLModelを使用して構築されており、テキストプロンプトや画像から回路図のYAML定義を生成するロジックを提供します。

## 技術スタック

-   **FastAPI**: Python製のWebフレームワーク。APIエンドポイントを提供します。
-   **SQLModel**: Python製のORM。データベースとの連携を簡素化します。
-   **PostgreSQL**: データベースとして利用します。
-   **uv**: Pythonのパッケージ管理ツール。
-   **Alembic**: データベースマイグレーションツール。

## 開発の始め方

プロジェクト全体の開発環境の起動については、[ルートのREADME.md](../README.md)を参照してください。

### 1. 依存関係のインストール (ローカル開発時)

Docker Composeを使用しないローカル環境でバックエンドを開発する場合、`uv`を使用して依存関係をインストールします。

```bash
cd backend
uv sync
source .venv/bin/activate
```

### 2. 開発サーバーの起動 (ローカル開発時)

```bash
cd backend
fastapi dev app/main.py
```

### 3. APIドキュメント

バックエンドAPIのインタラクティブなドキュメントは、開発サーバー起動後、以下のURLで確認できます。

-   **Swagger UI**: http://localhost:8000/docs
-   **ReDoc**: http://localhost:8000/redoc

## データベースマイグレーション

モデルの変更をデータベースに適用するには、Alembicを使用します。

1.  **バックエンドコンテナ内でBashセッションを開始:**
    ```bash
    docker compose exec backend bash
    ```
2.  **マイグレーションリビジョンの作成:**
    モデル（`app/models/`内のファイル）を変更した後、コンテナ内で以下のコマンドを実行します。
    ```bash
    alembic revision --autogenerate -m "変更内容の概要"
    ```
3.  **データベースのアップグレード:**
    作成したリビジョンをデータベースに適用します。
    ```bash
    alembic upgrade head
    ```

## テスト

バックエンドのテストはPytestを使用しています。

```bash
# プロジェクトルートから実行
docker compose exec backend bash scripts/test.sh
```

## 関連ファイル

-   `app/main.py`: FastAPIアプリケーションのエントリーポイント。
-   `app/api/routes/`: APIエンドポイントの定義。
-   `app/models/`: データベースモデルの定義。
-   `app/crud.py`: データベース操作（CRUD）ロジック。
-   `app/alembic/`: データベースマイグレーション関連ファイル。
