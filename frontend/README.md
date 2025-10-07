# CircuitCraft AI - フロントエンド

## プロジェクト概要

このディレクトリには、Circuit Craft AIアプリケーションのフロントエンドが含まれています。
React (Vite, TypeScript) と Chakra UI を使用して構築されており、ユーザーインターフェースを提供します。

## 技術スタック

-   **React**: UI構築のためのJavaScriptライブラリ。
-   **Vite**: 高速な開発サーバーとビルドツール。
-   **TypeScript**: 型安全なJavaScript。
-   **Chakra UI**: UIコンポーネントライブラリ。
-   **TanStack Query**: データフェッチとキャッシュ管理。
-   **TanStack Router**: ルーティング管理。

## 開発の始め方

プロジェクト全体の開発環境の起動については、[ルートのREADME.md](../README.md)を参照してください。

### 1. 依存関係のインストール (ローカル開発時)

Docker Composeを使用しないローカル環境でフロントエンドを開発する場合、Node.jsのバージョン管理ツール（fnmまたはnvm）を使用して依存関係をインストールします。

```bash
cd frontend
# .nvmrcに指定されたNode.jsバージョンをインストール・使用
fnm use --install # または nvm use --install
npm install
```

### 2. 開発サーバーの起動 (ローカル開発時)

```bash
cd frontend
npm run dev
```

開発サーバー起動後、ブラウザで http://localhost:5173/ にアクセスしてください。
コードの変更は自動的にリロードされます。

### 3. クライアントコードの生成

バックエンドのAPIスキーマが変更された場合、フロントエンドのクライアントコードを再生成する必要があります。

```bash
# プロジェクトルートから実行
./scripts/generate-client.sh
```

## コード構造

-   `src/`: フロントエンドの主要なコード。
-   `src/assets`: 静的アセット。
-   `src/client`: 自動生成されたAPIクライアント。
-   `src/components`: 再利用可能なUIコンポーネント。
-   `src/hooks`: カスタムフック。
-   `src/routes`: ページコンポーネントを含むルーティング定義。
-   `src/theme.tsx`: Chakra UIのカスタムテーマ定義。

## テスト

フロントエンドのテストはPlaywrightを使用しています。

```bash
# プロジェクトルートから実行
docker compose run --rm frontend-playwright
```

## 関連ファイル

-   `src/main.tsx`: アプリケーションのエントリーポイント。
-   `src/components/ui/provider.tsx`: Chakra UIのプロバイダー設定。
-   `vite.config.ts`: Viteの設定ファイル。
