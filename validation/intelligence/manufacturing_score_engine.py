from validation.intelligence.manufacturing_score import (
    ManufacturingScore,
)


class ManufacturingScoreEngine:

    def calculate(
        self,
        report
    ):

        score = 100

        score -= len(
            report.errors
        ) * 30

        score -= len(
            report.warnings
        ) * 10

        score -= len(
            report.recommendations
        ) * 2

        score = max(
            0,
            score
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

        return ManufacturingScore(
            score=score,
            grade=grade,
            explanation="Manufacturing quality score",
        )
