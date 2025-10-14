# app/models/__init__.py
from .circuit import Circuit, CircuitCreate, CircuitPublic, CircuitUpdate
from .file_content import FileContent
from .item import Item, ItemCreate, ItemPublic, ItemsPublic, ItemUpdate
from .msg import Message
from .token import NewPassword, Token, TokenPayload
from .user import (
    UpdatePassword,
    User,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)

# ここにすべてのモデルをインポート
# from .user import User
# from .item import Item

__all__ = [
    "Circuit",
    "CircuitCreate",
    "CircuitUpdate",
    "CircuitPublic",
    "User",
    "UserCreate",
    "UserUpdate",
    "UserPublic",
    "UsersPublic",
    "UpdatePassword",
    "UserRegister",
    "UserUpdateMe",
    "Item",
    "ItemCreate",
    "ItemUpdate",
    "ItemPublic",
    "ItemsPublic",
    "FileContent",
    "Token",
    "TokenPayload",
    "Message",
    "NewPassword",
]  # 必要なものをリストに追加
