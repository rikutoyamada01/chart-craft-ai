from app.services.formatters.base import FileFormatter


def test_file_formatter_importable() -> None:
    assert FileFormatter is not None
