# 回路図YAML仕様

このドキュメントは、回路図の構成要素、接続、プロパティ、および物理的なレイアウト情報を記述するためのYAMLフォーマットを定義します。このYAMLは、回路図の生成や管理に使用されることを想定しています。

## 1. 全体構造

YAMLのルート要素は`circuit`であり、その中に回路のメタ情報、コンポーネントの定義、および接続情報が含まれます。

```yaml
circuit:
  name: "回路名"
  description: "回路の説明"
  components:
    # コンポーネントのリスト
  connections:
    # 接続のリスト
```

## 2. `circuit`セクション

回路全体の基本的な情報を提供します。

*   `name` (string): 回路の名称。
*   `description` (string): 回路の簡単な説明。

## 3. `components`セクション

回路を構成する各要素（部品、ジャンクション、モジュールなど）を定義します。これはオブジェクトのリストです。

### 各コンポーネントの共通プロパティ

*   `id` (string, 必須): 回路内で一意なコンポーネントの識別子。
*   `type` (string, 必須): コンポーネントの種類（例: `resistor`, `led`, `battery`, `junction`, `module`, `power_supply`など）。
*   `properties` (object): コンポーネント固有の属性をキーバリュー形式で記述します。

### `properties`内の共通プロパティ

すべてのコンポーネントは、以下の物理レイアウト関連のプロパティを持つことができます。

*   `position` (object): コンポーネントの物理的な位置。
    *   `x` (number): X座標。
    *   `y` (number): Y座標。
*   `rotation` (number, オプション): コンポーネントの回転角度（度数）。デフォルトは0。

### `ports`プロパティ (コンポーネントが外部と接続するための端子)

一部のコンポーネント（特に`module`や`power_supply`など）は、外部との接続点として`ports`を持つことができます。

*   `ports` (list of objects):
    *   `name` (string): ポートの名称（例: `VCC`, `GND`, `input_power`）。
    *   `direction` (string, オプション): ポートの方向（例: `input`, `output`, `bidirectional`）。

### 特殊なコンポーネントの種類

#### `type: "junction"` (分岐点)

配線を分岐させるための仮想的なコンポーネントです。

*   `properties`: `position`以外の特別なプロパティは通常持ちません。`name`を追加することも可能です。

#### `type: "module"` (モジュール)

再利用可能なサブ回路を定義するためのコンポーネントです。モジュール自体が`components`と`connections`を持ちます。

*   `properties`:
    *   `name` (string): モジュールの名称。
    *   `ports` (list of objects): モジュールが外部回路と接続するためのポート。上記`ports`プロパティと同様の構造です。
*   `internal_components` (list of objects): モジュール内部に含まれるコンポーネントのリスト。トップレベルの`components`と同様の構造ですが、`position`はモジュールを基準とした相対位置になります。
*   `internal_connections` (list of objects): モジュール内部のコンポーネント間、およびモジュールの`ports`と内部コンポーネント間の接続を定義します。トップレベルの`connections`と同様の構造です。

## 4. `connections`セクション

回路内のコンポーネント間の接続を定義します。これはオブジェクトのリストです。

*   `source` (object): 接続の開始点。
    *   `component_id` (string): 接続元のコンポーネントの`id`。
    *   `terminal` (string, オプション): コンポーネントの特定の端子名（例: `positive`, `negative`, `anode`, `cathode`, `any`）。
    *   `port` (string, オプション): モジュールの外部ポート名。
*   `target` (object): 接続の終了点。
    *   `component_id` (string): 接続先のコンポーネントの`id`。
    *   `terminal` (string, オプション): コンポーネントの特定の端子名。
    *   `port` (string, オプション): モジュールの外部ポート名。

## 5. YAML構造の例

```yaml
circuit:
  name: "Complex Circuit with Modules and Branching"
  description: "モジュールと分岐配線を含む回路の例"

  components:
    # 通常のコンポーネント
    - id: "power_supply_1"
      type: "power_supply"
      properties:
        voltage: "5V"
        current_limit: "1A"
        position: { x: 50, y: 50 }
        rotation: 0
        ports:
          - name: "VCC"
            direction: "output"
          - name: "GND"
            direction: "output"

    # ジャンクション（分岐点）コンポーネント
    - id: "junction_A"
      type: "junction"
      properties:
        name: "分岐点A"
        position: { x: 150, y: 70 }

    # モジュールコンポーネント
    - id: "led_driver_module_1"
      type: "module"
      properties:
        name: "LED Driver Module"
        position: { x: 250, y: 100 }
        rotation: 90
        ports:
          - name: "input_power"
            direction: "input"
          - name: "output_led_anode"
            direction: "output"
          - name: "output_led_cathode"
            direction: "output"
      internal_components:
        - id: "resistor_internal_1"
          type: "resistor"
          properties:
            resistance: "220ohm"
            position: { x: 30, y: 20 }
            rotation: 0
        - id: "led_internal_1"
          type: "led"
          properties:
            color: "green"
            position: { x: 80, y: 20 }
            rotation: 0
        - id: "junction_internal_B"
          type: "junction"
          properties:
            position: { x: 50, y: 50 }
      internal_connections:
        - source: { component_id: "led_driver_module_1", port: "input_power" }
          target: { component_id: "resistor_internal_1", terminal: "any" }
        - source: { component_id: "resistor_internal_1", terminal: "other" }
          target: { component_id: "led_internal_1", terminal: "anode" }
        - source: { component_id: "led_internal_1", terminal: "cathode" }
          target: { component_id: "led_driver_module_1", port: "output_led_cathode" }

    # 通常のコンポーネント（モジュールから駆動されるLED）
    - id: "external_led_1"
      type: "led"
      properties:
        color: "blue"
        position: { x: 350, y: 150 }
        rotation: 0

  connections:
    # 電源からジャンクションへの接続
    - source: { component_id: "power_supply_1", port: "VCC" }
      target: { component_id: "junction_A", terminal: "any" }

    # ジャンクションからモジュールへの分岐接続
    - source: { component_id: "junction_A", terminal: "any" }
      target: { component_id: "led_driver_module_1", port: "input_power" }

    # モジュールから外部LEDへの接続
    - source: { component_id: "led_driver_module_1", port: "output_led_anode" }
      target: { component_id: "external_led_1", terminal: "anode" }
    - source: { component_id: "external_led_1", terminal: "cathode" }
      target: { component_id: "power_supply_1", port: "GND" }
```
