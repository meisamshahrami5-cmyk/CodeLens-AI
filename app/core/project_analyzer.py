from app.core.scanner import ProjectScanner
from app.core.analyzer import CodeAnalyzer
from app.core.quality import QualityAnalyzer
from app.core.security import SecurityAnalyzer
from app.core.score_engine import ScoreEngine


class ProjectAnalyzer:
    """Run the complete CodeLens AI analysis pipeline."""

    def __init__(self, project_path):
        self.project_path = project_path

    def analyze(self):

        scanner = ProjectScanner(
            self.project_path
        )

        files = scanner.scan()

        if not files:
            raise RuntimeError(
                "No Python files were found."
            )

        statistics = scanner.get_statistics()

        all_issues = []
        all_functions = []
        all_classes = []

        for file in files:

            result = CodeAnalyzer(
                file
            ).analyze()

            all_issues.extend(
                result["issues"]
            )

            all_functions.extend(
                result["functions"]
            )

            all_classes.extend(
                result["classes"]
            )

        ast_result = {
            "issues": all_issues,
            "functions": all_functions,
            "classes": all_classes,
        }

        quality_analyzer = QualityAnalyzer(
            self.project_path
        )

        quality_result = (
            quality_analyzer.analyze_project(
                files
            )
        )

        security_analyzer = SecurityAnalyzer(
            self.project_path
        )

        security_result = (
            security_analyzer.analyze()
        )

        score_engine = ScoreEngine(
            ast_result,
            quality_result,
            security_result,
        )

        scores = score_engine.calculate()

        return {
            "project": self.project_path,
            "files": files,
            "statistics": statistics,
            "ast": ast_result,
            "quality": quality_result,
            "security": security_result,
            "scores": scores,
        }