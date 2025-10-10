## 回路図生成の実装方針

`POST /circuits/definitions` で保存された `circuit_yaml` を基に、`GET /circuits/{circuit_id}/render` エンドポイントで実際の回路図を生成し、指定された形式で返却するための実装方針を以下に示します。

この実装は、`architecture.md`で定義された**Strategyパターン**に基づきます。

### 1. 回路定義のパース

*   **目的**: `circuit_yaml` (YAML形式の文字列) を、Pydanticモデルである `CircuitData` オブジェクトに変換します。
*   **ライブラリ**: `PyYAML` を使用します。
*   **詳細**:
    *   `circuit_yaml` を読み込み、`yaml.safe_load()` を使用して辞書に変換します。
    *   その辞書を `CircuitData` モデルに渡して、データのバリデーションと型変換を行います。
    *   パースやバリデーションでエラーが発生した場合は、適切なHTTPエラー（例: 400 Bad Request）を返します。

### 2. FileFormatterによるファイル生成

*   **目的**: パースされた `CircuitData` オブジェクトから、リクエストされた形式のファイル（`FileContent`オブジェクト）を生成します。
*   **アーキテクチャ**:
    *   `architecture.md`で定義されている通り、ファイル生成は`FileFormatter`インターフェースを実装した具体的なクラス（フォーマッター）が担当します。
    *   中心となるサービス（例: `CircuitGeneratorService`）が、リクエストされた`format`（`svg`, `png`など）に応じて適切なフォーマッターを選択し、その`.format(data: CircuitData)`メソッドを呼び出します。

#### 具体的なフォーマッターの実装例

*   **`SvgFormatter`**:
    *   **責務**: `CircuitData`からSVG形式の文字列を生成します。
    *   **ライブラリ**: `svgwrite` を使用して、Pythonコードからプログラム的にSVG要素を構築します。
    *   **詳細**: `format`メソッド内で`svgwrite.Drawing`オブジェクトを作成し、`CircuitData`に含まれるコンポーネントや接続線の情報を基にSVGを描画します。

*   **`PngFormatter` / `PdfFormatter`**:
    *   **責務**: `CircuitData`からPNGやPDF形式のバイナリデータを生成します。
    *   **ライブラリ**: `CairoSVG` を使用します。
    *   **詳細**: これらのフォーマッターは、内部でまず`SvgFormatter`を呼び出してSVGデータを生成し、その結果を`CairoSVG.svg2png()`や`CairoSVG.svg2pdf()`に渡して目的の形式に変換する、という実装が考えられます。これにより、描画ロジックの一元化が図れます。

### 3. 必要なライブラリ

上記の実装には、以下のPythonライブラリが必要です。これらは `backend/pyproject.toml` の `dependencies` セクションに追加されます。

*   `PyYAML`
*   `svgwrite`
*   `CairoSVG` (依存ライブラリとして `cairo` が必要になる場合があります)
