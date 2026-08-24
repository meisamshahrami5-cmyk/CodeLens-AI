import json
import subprocess
import sys
from pathlib import Path


class SecurityAnalyzer:
    """Run Bandit security analysis on a Python project."""

    def __init__(self, project_path):
        self.project_path = Path(project_path)

    def analyze(self):
        if not self.project_path.exists():
            raise FileNotFoundError(
                f"Project not found: {self.project_path}"
            )

        command = [
            sys.executable,
            "-m",
            "bandit",
            "-r",
            str(self.project_path),
            "-f",
            "json",
            "-q",
        ]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
            )

        except Exception as error:
            return {
                "success": False,
                "issues": [],
                "metrics": {},
                "error": str(error),
            }

        # Bandit can return non-zero when vulnerabilities are found.
        if not result.stdout.strip():
            return {
                "success": False,
                "issues": [],
                "metrics": {},
                "error": result.stderr.strip() or "No Bandit output.",
            }

        try:
            data = json.loads(result.stdout)

        except json.JSONDecodeError:
            return {
                "success": False,
                "issues": [],
                "metrics": {},
                "error": "Could not parse Bandit output.",
            }

        issues = []

        for item in data.get("results", []):
            issues.append({
                "test_id": item.get("test_id"),
                "test_name": item.get("test_name"),
                "severity": item.get("issue_severity"),
                "confidence": item.get("issue_confidence"),
                "file": item.get("filename"),
                "line": item.get("line_number"),
                "message": item.get("issue_text"),
            })

        return {
            "success": True,
            "issues": issues,
            "metrics": data.get("metrics", {}),
            "error": None,
        }