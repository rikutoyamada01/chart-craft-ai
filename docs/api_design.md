## 9. API設計

これまでの議論に基づき、回路図の生成とエクスポートを行うAPIの設計案を以下に示します。

**ベースURL**: `/api/v1`

### 9.1. 回路定義の管理と図の生成 (改訂版)

回路定義の管理と図の生成をより柔軟かつ効率的に行うため、以下の2つのエンドポイントを導入します。

#### 9.1.1. 回路定義の保存

*   **エンドポイント**: `POST /circuits/definitions`
*   **説明**: 提供されたYAML形式の回路定義をバックエンドに保存し、一意の識別子 (`circuit_id`) を返却します。この `circuit_id` を使用して、後続の図の生成リクエストを行うことができます。
*   **リクエストボディ**:
    *   `Content-Type`: `application/json`
    *   **例**:
        ```json
        {
          "circuit_yaml": "circuit:\n  name: \"Simple LED Circuit\"\n  components:\n    - id: \"battery_1\"\n      type: \"battery\"\n      properties:\n        voltage: \"1.5V\"\n        position: { x: 10, y: 10 }\n  connections:\n    - from: { component_id: \"battery_1\", terminal: \"positive\" }\n      to: { component_id: \"battery_1\", terminal: \"negative\" }\n"
        }
        ```
    *   `circuit_yaml` (string, 必須): 回路定義を記述したYAML文字列。
*   **レスポンス**:
    *   `201 Created`: 回路定義が正常に保存された場合。
        *   `Content-Type`: `application/json`
        *   **例**:
            ```json
            {
              "circuit_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef"
            }
            ```
        *   `circuit_id` (string): 保存された回路定義の一意の識別子 (UUID)。
    *   `400 Bad Request`: リクエストボディのYAMLが無効な場合。
        *   **例**:
            ```json
            {
              "detail": "Invalid circuit YAML.",
              "errors": ["YAML parsing error: ..."]
            }
            ```
    *   `500 Internal Server Error`: サーバー内部で予期せぬエラーが発生した場合。

#### 9.1.2. 回路図のレンダリング

*   **エンドポイント**: `GET /circuits/{circuit_id}/render`
*   **説明**: 指定された `circuit_id` に対応する回路定義から回路図を生成し、指定された形式で返却します。
*   **パスパラメータ**:
    *   `circuit_id` (string, 必須): レンダリングする回路定義の識別子。
*   **クエリパラメータ**:
    *   `format` (string, オプション): 出力形式。
        *   許容値: `svg` (デフォルト), `png`, `pdf`
    *   `width` (integer, オプション): `png`形式の場合の画像幅（ピクセル）。指定がない場合はデフォルト値を使用。
    *   `height` (integer, オプション): `png`形式の場合の画像高さ（ピクセル）。指定がない場合はデフォルト値を使用。
*   **レスポンス**:
    *   `200 OK`:
        *   `Content-Type`: `image/svg+xml` (SVGの場合), `image/png` (PNGの場合), `application/pdf` (PDFの場合)
        *   `Body`: 生成された画像またはドキュメントのバイナリデータ。
    *   `404 Not Found`: 指定された `circuit_id` が見つからない場合。
        *   **例**:
            ```json
            {
              "detail": "Circuit definition not found."
            }
            ```
    *   `400 Bad Request`: サポートされていない`format`が指定された場合。
        *   **例**:
            ```json
              "detail": "Unsupported format: 'jpeg'."
            }
            ```
    *   `500 Internal Server Error`: サーバー内部で予期せぬエラーが発生した場合。

### 9.2. 回路定義のバリデーション

*   **エンドポイント**: `POST /circuits/validate`
*   **説明**: 提供されたYAML形式の回路定義が、定義されたスキーマに準拠しているかを検証します。
*   **リクエストボディ**:
    *   `Content-Type`: `application/json`
    *   **例**:
        ```json
        {
          "circuit_yaml": "circuit:\n  name: \"Simple LED Circuit\"\n  components:\n    - id: \"battery_1\"\n      type: \"battery\"\n      properties:\n        voltage: \"1.5V\"\n        position: { x: 10, y: 10 }\n"
        }
        ```
    *   `circuit_yaml` (string, 必須): 回路定義を記述したYAML文字列。
*   **レスポンス**:
    *   `200 OK`: YAMLが有効な場合。
        *   **例**:
            ```json
            {
              "status": "valid",
              "message": "Circuit YAML is valid."
            }
            ```
    *   `400 Bad Request`: YAMLが無効な場合。
        *   **例**:
            ```json
            {
              "status": "invalid",
              "message": "Circuit YAML is invalid.",
              "errors": ["Validation error: Missing 'connections' section.", "Validation error: Component 'resistor_1' has invalid 'resistance' value."]
            }
            ```

### 9.3. その他の考慮事項

*   **認証・認可**: 本設計には含まれていませんが、本番環境ではAPIキーやOAuth2などの認証・認可メカニズムが必要です。
*   **非同期処理**: 非常に複雑な回路のレンダリングには時間がかかる場合があります。新しい設計では、`POST /circuits/definitions` で回路定義を保存し、`circuit_id` を取得した後、`GET /circuits/{circuit_id}/render` を呼び出すことでレンダリングを行います。レンダリング処理が長時間にわたる場合、`GET /circuits/{circuit_id}/render` はジョブIDを返し、`GET /circuits/status/{job_id}`や`GET /circuits/result/{job_id}`のような非同期APIパターンを検討することも可能です。
*   **スキーマ定義**: `validate`エンドポイントの実現には、回路YAMLの厳密なスキーマ（例: JSON Schema）を定義する必要があります。
