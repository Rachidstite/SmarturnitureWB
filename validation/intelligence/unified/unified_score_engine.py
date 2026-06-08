from validation.intelligence.unified.unified_score import (
    UnifiedScore,
)


class UnifiedScoreEngine:

    def calculate(
        self,
        report,
    ):

        score = 100

        score -= len(
            getattr(
                report,
                "warnings",
                [],
            )
        ) * 5

        score -= len(
            getattr(
                report,
                "errors",
                [],
            )
        ) * 30

        score = max(
            0,
            score,
        )

        if score >= 95:
            grade = "A+"
        elif score >= 90:
            grade = "A"
        elif score >= 80:
            grade = "B"
        elif score >= 70:
            grade = "C"
        elif score >= 60:
            grade = "D"
        else:
            grade = "F"

        return UnifiedScore(
            score=score,
            grade=grade,
            explanation="Project intelligence score",
        )
