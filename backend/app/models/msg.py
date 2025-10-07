from sqlmodel import Field, SQLModel


# Generic message
class Message(SQLModel):
    message: str
