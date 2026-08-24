class ScoreEngine:
    """Calculate CodeLens AI project scores."""

    def __init__(self, ast_result, quality_result, security_result):
        self.ast_result = ast_result
        self.quality_result = quality_result
        self.security_result = security_result

    def calculate(self):
        maintainability_score = self._maintainability_score()
        complexity_score = self._complexity_score()
        issue_score = self._issue_score()
        security_score = self._security_score()

        code_quality = round(
            (
                maintainability_score * 0.40
                + complexity_score * 0.30
                + issue_score * 0.30
            )
        )

        overall_score = round(
            code_quality * 0.70
            + security_score * 0.30
        )

        return {
            "overall": overall_score,
            "code_quality": code_quality,
            "security": security_score,
            "maintainability": maintainability_score,
            "complexity": complexity_score,
            "issues": issue_score,
            "grade": self._grade(overall_score),
        }

    # ---------------------------------------------------------
    # Maintainability
    # ---------------------------------------------------------

    def _maintainability_score(self):
        value = self.quality_result.get(
            "average_maintainability",
            0,
        )

        if value <= 0:
            return 0

        # Radon's maintainability index is normally 0-100.
        return max(0, min(100, round(value)))

    # ---------------------------------------------------------
    # Complexity
    # ---------------------------------------------------------

    def _complexity_score(self):
        complexity_items = self.quality_result.get(
            "complexity",
            [],
        )

        if not complexity_items:
            return 100

        penalties = 0

        for item in complexity_items:
            complexity = item.get("complexity", 1)

            if complexity <= 5:
                penalties += 0

            elif complexity <= 10:
                penalties += 5

            elif complexity <= 20:
                penalties += 10

            elif complexity <= 30:
                penalties += 20

            elif complexity <= 40:
                penalties += 30

            else:
                penalties += 40

        score = 100 - penalties

        return max(0, score)

    # ---------------------------------------------------------
    # AST Issues
    # ---------------------------------------------------------

    def _issue_score(self):
        issues = self.ast_result.get(
            "issues",
            [],
        )

        score = 100

        penalties = {
            "Critical": 25,
            "High": 15,
            "Medium": 8,
            "Low": 3,
            "Info": 1,
        }

        for issue in issues:
            severity = issue.get(
                "severity",
                "Info",
            )

            score -= penalties.get(
                severity,
                1,
            )

        return max(0, score)

    # ---------------------------------------------------------
    # Security
    # ---------------------------------------------------------

    def _security_score(self):
        issues = self.security_result.get(
            "issues",
            [],
        )

        score = 100

        penalties = {
            "HIGH": 25,
            "MEDIUM": 12,
            "LOW": 5,
        }

        for issue in issues:
            severity = str(
                issue.get(
                    "severity",
                    "LOW",
                )
            ).upper()

            score -= penalties.get(
                severity,
                2,
            )

        return max(0, score)

    # ---------------------------------------------------------
    # Grade
    # ---------------------------------------------------------

    @staticmethod
    def _grade(score):
        if score >= 90:
            return "A"

        if score >= 80:
            return "B"

        if score >= 70:
            return "C"

        if score >= 60:
            return "D"

        if score >= 50:
            return "E"

        return "F"