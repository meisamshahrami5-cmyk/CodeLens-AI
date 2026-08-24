from pathlib import Path

from radon.complexity import cc_visit
from radon.metrics import mi_visit


class QualityAnalyzer:
    """Analyze Python code quality using Radon 6."""

    def __init__(self, project_path):
        self.project_path = Path(project_path)

    def analyze_file(self, file_path):
        file_path = Path(file_path)

        try:
            source = file_path.read_text(
                encoding="utf-8",
                errors="ignore",
            )
        except OSError as error:
            return {
                "file": str(file_path),
                "complexity": [],
                "maintainability": None,
                "error": str(error),
            }

        try:
            complexity_data = cc_visit(source)

            complexity = []

            for item in complexity_data:
                # Radon 6 uses different object types for
                # functions and classes.
                item_type = type(item).__name__

                if item_type == "Class":
                    code_type = "Class"
                elif item_type in ("Function", "Method"):
                    code_type = "Function"
                else:
                    code_type = item_type

                complexity.append({
                    "name": item.name,
                    "type": code_type,
                    "line": item.lineno,
                    "complexity": item.complexity,
                    "rank": self._complexity_rank(
                        item.complexity
                    ),
                })

            maintainability = mi_visit(
                source,
                multi=True,
            )

            return {
                "file": str(file_path),
                "complexity": complexity,
                "maintainability": round(
                    maintainability,
                    2,
                ),
                "error": None,
            }

        except Exception as error:
            return {
                "file": str(file_path),
                "complexity": [],
                "maintainability": None,
                "error": str(error),
            }

    @staticmethod
    def _complexity_rank(value):
        if value <= 5:
            return "A"
        elif value <= 10:
            return "B"
        elif value <= 20:
            return "C"
        elif value <= 30:
            return "D"
        elif value <= 40:
            return "E"
        else:
            return "F"

    def analyze_project(self, files):
        results = []

        for file_path in files:
            results.append(
                self.analyze_file(file_path)
            )

        valid_scores = [
            result["maintainability"]
            for result in results
            if result["maintainability"] is not None
        ]

        average_maintainability = (
            sum(valid_scores) / len(valid_scores)
            if valid_scores
            else 0
        )

        complexity_items = []

        for result in results:
            complexity_items.extend(
                result["complexity"]
            )

        return {
            "files": results,
            "average_maintainability": round(
                average_maintainability,
                2,
            ),
            "complexity": complexity_items,
        }