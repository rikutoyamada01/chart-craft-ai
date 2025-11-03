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

### 3. SvgFormatterの拡張性改善リファクタリング

旧来の`SvgFormatter`は、コンポーネントの描画ロジックを直接内部に持っており、新しいコンポーネントタイプを追加するたびに`SvgFormatter`自体を修正する必要がありました。これは可読性、保守性、拡張性の低下を招くため、Strategy/Factoryパターンを導入し、コンポーネントごとの描画ロジックを分離しました。

**目標:**
*   `SvgFormatter`の単一責任の原則への準拠を強化する。
*   新しいコンポーネントタイプを追加する際の`SvgFormatter`の修正を不要にする（オープン/クローズドの原則）。
*   コンポーネントごとの描画ロジックの可読性と保守性を向上させる。

**アーキテクチャ:**

1.  **`CircuitExporter`へのリネーム:**
    *   パースとフォーマットのオーケストレーションという広い責任を持っていた`CircuitRenderer`クラスを、より役割を正確に表す`CircuitExporter`にリネームしました。

2.  **`SvgComponentRenderer`抽象基底クラスの導入:**
    *   各コンポーネントタイプがSVGを描画するための共通インターフェースとして`SvgComponentRenderer`を定義しました。

3.  **具体的な`SvgComponentRenderer`実装:**
    *   各コンポーネントタイプ（`junction`, `resistor`, `led`, `battery`）ごとに、`SvgComponentRenderer`を継承した専用のクラスを作成し、そのコンポーネントの描画ロジックをカプセル化しました。

4.  **`SvgComponentRendererFactory`の導入:**
    *   コンポーネントの`type`に基づいて、適切な`SvgComponentRenderer`インスタンスを提供するファクトリクラスを導入しました。これにより、`SvgFormatter`は特定のコンポーネントレンダラーの実装に依存しなくなりました。

**実装内容:**

1.  **`CircuitExporter`へのリネーム:** `CircuitRenderer`を`CircuitExporter`にリネームし、関連するすべての参照を更新しました。

2.  **ディレクトリの作成:** `backend/app/services/renderers/` ディレクトリを作成しました。

3.  **抽象基底クラスの定義:** `backend/app/services/renderers/svg_component_renderer.py` に `SvgComponentRenderer` 抽象基底クラスを定義しました。

4.  **具体的なコンポーネントレンダラーの実装:**
    *   `backend/app/services/renderers/junction_svg_renderer.py` に `JunctionSvgRenderer` を実装しました。
    *   `backend/app/services/renderers/resistor_svg_renderer.py` に `ResistorSvgRenderer` を実装しました。
    *   `backend/app/services/renderers/led_svg_renderer.py` に `LedSvgRenderer` を実装しました。
    *   `backend/app/services/renderers/battery_svg_renderer.py` に `BatterySvgRenderer` を実装しました。

5.  **ファクトリの実装:** `backend/app/services/renderers/svg_component_renderer_factory.py` に `SvgComponentRendererFactory` を実装し、すべての具象レンダラーを登録しました。

6.  **`SvgFormatter`の修正:** `backend/app/services/formatters/svg_formatter.py` を修正し、`SvgComponentRendererFactory` を使用して各コンポーネントの描画を委譲するように変更しました。

7.  **テストの更新:** 新しいレンダリングアーキテクチャをカバーするようにテストを更新・追加し、すべてのテストがパスすることを確認しました。



### 4. 必要なライブラリ

上記の実装には、以下のPythonライブラリが必要です。これらは `backend/pyproject.toml` の `dependencies` セクションに追加されます。

*   `PyYAML`
*   `svgwrite`
*   `CairoSVG` (依存ライブラリとして `cairo` が必要になる場合があります)
