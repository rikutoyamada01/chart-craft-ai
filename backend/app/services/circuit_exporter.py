import yaml
from fastapi import HTTPException

from app.models.circuit import CircuitData
from app.models.file_content import FileContent
from app.services.formatters.svg_formatter import SvgFormatter


class CircuitExporter:
    def render(self, circuit_data: CircuitData, format: str = "svg") -> FileContent:
        """
        Renders a circuit diagram from CircuitData.
        """
        if format.lower() != "svg":
            raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")

        # In the future, we can have a factory here to choose the formatter
        # based on the 'format' parameter.
        formatter = SvgFormatter()
        file_content = formatter.format(circuit_data)
        return file_content

    def render_from_yaml(self, yaml_data: str, format: str = "svg") -> FileContent:
        """
        Parses YAML data and renders a circuit diagram.
        """
        try:
            yaml_dict = yaml.safe_load(yaml_data)
            circuit_data = CircuitData.model_validate(yaml_dict)
        except (yaml.YAMLError, ValueError) as e:
            raise HTTPException(status_code=400, detail=f"Invalid YAML or data: {e}")

        return self.render(circuit_data, format)


circuit_exporter = CircuitExporter()
