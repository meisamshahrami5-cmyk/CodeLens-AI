from pathlib import Path


class ProjectScanner:
    """Scan a Python project and collect source files."""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)

    def scan(self):
        if not self.project_path.exists():
            raise FileNotFoundError(
                f"Project not found: {self.project_path}"
            )

        if not self.project_path.is_dir():
            raise NotADirectoryError(
                f"Path is not a directory: {self.project_path}"
            )

        python_files = []

        for file in self.project_path.rglob("*.py"):
            # Ignore virtual environments and cache directories
            ignored_parts = {
                ".venv",
                "venv",
                "__pycache__",
                ".git",
                "node_modules",
            }

            if any(part in ignored_parts for part in file.parts):
                continue

            python_files.append(file)

        return sorted(python_files)

    def get_statistics(self):
        files = self.scan()

        total_lines = 0
        total_code_lines = 0
        total_blank_lines = 0

        for file in files:
            try:
                content = file.read_text(
                    encoding="utf-8",
                    errors="ignore"
                )
            except OSError:
                continue

            lines = content.splitlines()

            total_lines += len(lines)

            for line in lines:
                stripped = line.strip()

                if not stripped:
                    total_blank_lines += 1
                else:
                    total_code_lines += 1

        return {
            "files": len(files),
            "total_lines": total_lines,
            "code_lines": total_code_lines,
            "blank_lines": total_blank_lines,
        }