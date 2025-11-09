from abc import ABC, abstractmethod
from typing import Any


class YamlGenerator(ABC):
    """YAML generator interface."""

    @abstractmethod
    def generate(self, input_data: Any) -> str:
        """
        Generates a YAML cir
        cuit definition from the given input data.

        :param input_data: The input data for the generator (e.g., a text prompt or an image file).
        :return: The generated YAML string.
        """
        pass
