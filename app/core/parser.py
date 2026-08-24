import ast
from pathlib import Path


class PythonParser:
    """Parse Python files using the built-in AST module."""

    def __init__(self, file_path):
        self.file_path = Path(file_path)

    def read_source(self):
        return self.file_path.read_text(
            encoding="utf-8",
            errors="ignore"
        )

    def parse(self):
        source = self.read_source()

        try:
            tree = ast.parse(
                source,
                filename=str(self.file_path)
            )

            return {
                "tree": tree,
                "source": source,
                "error": None,
            }

        except SyntaxError as error:
            return {
                "tree": None,
                "source": source,
                "error": {
                    "message": error.msg,
                    "line": error.lineno,
                    "column": error.offset,
                },
            }