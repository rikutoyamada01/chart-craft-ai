from fastapi import APIRouter

from app.models.circuit import CircuitGenerationResponse

router = APIRouter()


@router.post("/generate", response_model=CircuitGenerationResponse)
def generate_circuit() -> CircuitGenerationResponse:
    """
    ユーザーからの文章(prompt)を受け取り、回路データを生成するエンドポイント
    """

    # TODO: ここで実際にAIを呼び出し、YAMLを生成する処理を実装する

    # 今は、受け取った文章をそのまま返すダミーの応答を作成
    dummy_yaml = """
components:
  - id: sample
    type: Resistor
connections:
  - from: nodeA
    to: nodeB
"""
    return CircuitGenerationResponse(
        message="回路データの生成に成功しました（これはダミーです）",
        yaml_data=dummy_yaml,
    )
