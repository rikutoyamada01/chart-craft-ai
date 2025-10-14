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

### 3. SvgFormatterの拡張性改善リファクタリング計画

現在の`SvgFormatter`は、コンポーネントの描画ロジックを直接内部に持っており、新しいコンポーネントタイプを追加するたびに`SvgFormatter`自体を修正する必要があります。これは可読性、保守性、拡張性の低下を招きます。この問題を解決するため、Strategy/Factoryパターンを導入し、コンポーネントごとの描画ロジックを分離します。

**目標:**
*   `SvgFormatter`の単一責任の原則への準拠を強化する。
*   新しいコンポーネントタイプを追加する際の`SvgFormatter`の修正を不要にする（オープン/クローズドの原則）。
*   コンポーネントごとの描画ロジックの可読性と保守性を向上させる。

**提案するアーキテクチャ:**

1.  **`CircuitExporter`へのリネーム:**
    *   現在の`CircuitRenderer`クラスは、パースとフォーマットのオーケストレーションという広い責任を持つため、より役割を正確に表す`CircuitExporter`にリネームします。

2.  **`SvgComponentRenderer`抽象基底クラスの導入:**
    *   各コンポーネントタイプがSVGを描画するための共通インターフェースを定義します。

3.  **具体的な`SvgComponentRenderer`実装:**
    *   各コンポーネントタイプ（例: `resistor`, `led`, `junction`）ごとに、`SvgComponentRenderer`を継承した専用のクラスを作成し、そのコンポーネントの描画ロジックをカプセル化します。これらのレンダラーは、`CircuitData.Component`の`properties`フィールドからコンポーネント固有の情報を取得して描画を行います。

4.  **`SvgComponentRendererFactory`の導入:**
    *   コンポーネントの`type`に基づいて、適切な`SvgComponentRenderer`インスタンスを提供するファクトリクラスを導入します。これにより、`SvgFormatter`は特定のコンポーネントレンダラーの実装に依存しなくなります。

**詳細な手順:**

1.  **ディレクトリの作成:**
    *   `backend/app/services/renderers/` ディレクトリを作成します。

2.  **抽象基底クラスの定義:**
    *   `backend/app/services/renderers/svg_component_renderer.py` に `SvgComponentRenderer` 抽象基底クラスを定義します。

3.  **具体的なコンポーネントレンダラーの実装:**
    *   `backend/app/services/renderers/junction_svg_renderer.py` に `JunctionSvgRenderer` を実装します。
    *   `backend/app/services/renderers/resistor_svg_renderer.py` に `ResistorSvgRenderer` を実装します（例として）。
    *   `backend/app/services/renderers/led_svg_renderer.py` に `LedSvgRenderer` を実装します（例として）。
    *   必要に応じて、他のコンポーネントタイプ（例: `battery`, `module`）のレンダラーも同様に実装します。

4.  **ファクトリの実装:**
    *   `backend/app/services/renderers/svg_component_renderer_factory.py` に `SvgComponentRendererFactory` を実装します。このファクトリは、各コンポーネントレンダラーを登録し、`component.type`に基づいて適切なレンダラーを提供します。

5.  **`SvgFormatter`の修正:**
    *   `backend/app/services/formatters/svg_formatter.py` を修正し、`SvgComponentRendererFactory` を使用して各コンポーネントの描画を委譲するようにします。`SvgFormatter`は、コンポーネントの描画ロジックを直接持つ代わりに、ファクトリから取得したレンダラーの`render`メソッドを呼び出すだけになります。
    *   接続線の描画ロジックも、コンポーネントレンダラーが提供するポート情報などを利用するように洗練することを検討します。

6.  **`CircuitRenderer`のリネーム:**
    *   `backend/app/services/circuit_renderer.py` のクラス名を `CircuitExporter` に変更します。
    *   関連するインポート（例: `backend/app/api/routes/circuits.py`）も更新します。

7.  **依存関係の更新:**
    *   `backend/pyproject.toml` に、必要に応じて新しいライブラリ（例: テンプレートエンジンなど）を追加します。

8.  **テストの更新:**
    *   新しいレンダリングアーキテクチャをカバーするように、既存のテストを更新し、必要に応じて新しいテストを追加します。

### 3.1. `CircuitRenderer`から`CircuitExporter`へのリネーム計画

`CircuitRenderer`クラスは、その責任範囲（YAMLパースのオーケストレーションとファイル形式への変換）をより正確に反映するため、`CircuitExporter`にリネームします。

**影響範囲:**

1.  **`backend/app/services/circuit_renderer.py`**:
    *   ファイル名自体を `backend/app/services/circuit_exporter.py` に変更します。
    *   クラス定義を `class CircuitRenderer:` から `class CircuitExporter:` に変更します。
    *   インスタンス作成を `circuit_renderer = CircuitRenderer()` から `circuit_exporter = CircuitExporter()` に変更します。

2.  **`backend/app/api/routes/circuits.py`**:
    *   インポート文を `from app.services.circuit_renderer import circuit_renderer` から `from app.services.circuit_exporter import circuit_exporter` に変更します。
    *   使用箇所を `circuit_renderer.render_from_yaml(...)` から `circuit_exporter.render_from_yaml(...)` に変更します。

3.  **`backend/tests/api/routes/test_circuits.py`**:
    *   インポート文を `from app.services.circuit_renderer import circuit_renderer` から `from app.services.circuit_exporter import circuit_exporter` に変更します。
    *   使用箇所を `circuit_renderer.render_from_yaml(...)` から `circuit_exporter.render_from_yaml(...)` に変更します。

4.  **`docs/circuit_rendering_implementation.md`**:
    *   このドキュメント内の`CircuitRenderer`への言及をすべて`CircuitExporter`に更新します。
    *   特に、「3. SvgFormatterの拡張性改善リファクタリング計画」セクションの「1. `CircuitExporter`へのリネーム」の記述を、リネームが完了したことを反映するように更新します。

**リネーム手順:**

1.  **ファイルのリネーム:**
    *   `backend/app/services/circuit_renderer.py` を `backend/app/services/circuit_exporter.py` にリネームします。
2.  **`backend/app/services/circuit_exporter.py` の内容修正:**
    *   `class CircuitRenderer:` を `class CircuitExporter:` に変更します。
    *   `circuit_renderer = CircuitRenderer()` を `circuit_exporter = CircuitExporter()` に変更します。
3.  **`backend/app/api/routes/circuits.py` の修正:**
    *   インポート文と使用箇所を更新します。
4.  **`backend/tests/api/routes/test_circuits.py` の修正:**
    *   インポート文と使用箇所を更新します。
5.  **`docs/circuit_rendering_implementation.md` の修正:**
    *   このドキュメント内の`CircuitRenderer`への言及を`CircuitExporter`に更新し、リネームが完了したことを明記します。

### 4. 必要なライブラリ

上記の実装には、以下のPythonライブラリが必要です。これらは `backend/pyproject.toml` の `dependencies` セクションに追加されます。

*   `PyYAML`
*   `svgwrite`
*   `CairoSVG` (依存ライブラリとして `cairo` が必要になる場合があります)
