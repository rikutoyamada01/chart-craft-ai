from pydantic import BaseModel


class FileContent(BaseModel):
    filename: str
    content: str
    mime_type: str
