from pydantic import BaseModel

class CircuitGenerationRequest(BaseModel):
    """回路生成リクエストのデータモデル"""
    prompt: str

class CircuitGenerationResponse(BaseModel):
    """回路生成レスポンスのデータモデル（今はダミー）"""
    message: str
    yaml_data: str
