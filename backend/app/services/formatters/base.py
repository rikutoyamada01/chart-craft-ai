from abc import ABC, abstractmethod

from app.models.circuit import CircuitData
from app.models.file_content import FileContent


class FileFormatter(ABC):
    @abstractmethod
    def format(self, data: CircuitData) -> FileContent:
        """
        CircuitDataを受け取り、特定のファイル形式のコンテンツを生成する。
        """
        pass
