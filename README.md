# Circuit Craft AI Project

## プロジェクト概要

Circuit Craft AIは、テキストプロンプトから回路図のYAML定義を生成するアプリケーションです。
バックエンドはFastAPI、フロントエンドはReact (Chakra UI) で構築されています。

## 開発の始め方

このプロジェクトはDocker Composeを使用して開発環境を構築します。

### 1. リポジリトのクローン

```bash
git clone https://github.com/rikutoyamada01/circuit-craft-ai
cd circuit-craft-ai
```

### 2. 環境設定ファイル (`.env`) の準備

プロジェクトルートにある`.env.example`をコピーして`.env`ファイルを作成し、必要に応じて設定を更新してください。

```bash
cp .env.example .env
# .env ファイルをエディタで開き、SECRET_KEY, POSTGRES_PASSWORD などを設定
```

### 3. Docker Compose の起動

開発環境を起動します。

```bash
docker compose watch
```

起動後、以下のURLでアクセスできます。
- **フロントエンド:** http://localhost:5173
- **バックエンドAPI (Swagger UI):** http://localhost:8000/docs

### 4. 開発の停止

```bash
docker compose down
```

## 共同開発ガイドライン

スムーズな開発のために、以下のガイドラインを設けます。

### 1. ブランチ戦略

- `main`ブランチは常に安定した状態を保ちます。
- 新しい機能開発やバグ修正は、`feature/機能名`や`bugfix/バグ名`のようなブランチを作成して行います。
- `main`ブランチへのマージはプルリクエスト (PR) 経由で行い、必ずレビューを必須とします。

### 2. コミットメッセージ

[Conventional Commits](https://www.conventionalcommits.org/ja/v1.0.0/) に従います。
例:
- `feat: 新機能の追加`
- `fix: バグの修正`
- `refactor: コードのリファクタリング`
- `docs: ドキュメントの更新`

### 3. コードスタイルとリンティング

`biome`と`ruff`を使用しています。コミット前に自動でチェック・修正されますが、開発中も以下のコマンドで手動チェック・修正が可能です。

```bash
# フロントエンド
npm run lint

# バックエンド
ruff check .
ruff format .
```

### 4. コードレビュー

プルリクエストを作成したら、必ず他のメンバーにレビューを依頼してください。
レビューでは、コードの品質、設計、テスト、規約への準拠などを確認します。

### 5. テスト

- 新しい機能を追加したり、バグを修正したりした場合は、必ず関連するテスト（ユニットテスト、結合テストなど）を作成または更新してください。
- テストは以下のコマンドで実行できます。
  ```bash
  # バックエンド
  docker compose run --rm backend bash scripts/test.sh

  # フロントエンド (Playwright)
  docker compose run --rm frontend-playwright
  ```

### 6. コミュニケーション

- 疑問点や相談事項があれば、積極的に共有しましょう。

### 7. GitHub Issues の活用

- **バグ報告:** 不具合を発見したら、詳細な再現手順、期待される動作、実際の動作を記述してIssueを作成してください。
- **機能要望:** 新しい機能のアイデアがあれば、その機能が解決する問題や期待される効果を記述してIssueを作成してください。
- **タスク管理:** 開発作業を細分化し、各タスクをIssueとして登録します。担当者を割り当て、進捗状況を明確にします。
- **ラベルの活用:** `bug`, `feature`, `enhancement`, `documentation`, `help wanted`などのラベルを活用し、Issueの種類を明確にします。

### 8. GitHub Projects の活用

- GitHub Projects (Projects (beta) または Projects (classic)) を使用して、開発の進捗を視覚的に管理します。
- IssueやプルリクエストをProjectのボードに追加し、`Todo`, `In Progress`, `Done`などのステータスで管理します。
- 各タスクの依存関係や優先順位を明確にし、チーム全体の開発状況を把握します。

### 9. Issueとプルリクエストの連携

- プルリクエストを作成する際は、関連するIssueをリンクしてください。
- コミットメッセージやプルリクエストの説明に `Fixes #Issue番号` や `Closes #Issue番号` を含めることで、PRのマージ時に自動的にIssueをクローズできます。
