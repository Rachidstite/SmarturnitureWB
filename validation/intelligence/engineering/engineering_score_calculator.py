from validation.intelligence.engineering.engineering_score import (
    EngineeringScore,
)


class EngineeringScoreCalculator:

    def calculate(
        self,
        warnings,
        errors,
    ):

        score = 100

        score -= len(warnings) * 5
        score -= len(errors) * 15

        score = max(
            0,
            score,
        )

        if score >= 95:
            grade = "A+"
        elif score >= 90:
            grade = "A"
        elif score >= 80:
            grade = "B+"
        elif score >= 70:
            grade = "B"
        elif score >= 60:
            grade = "C"
        elif score >= 50:
            grade = "D"
        else:
            grade = "F"

        return EngineeringScore(
            score=score,
            grade=grade,
            explanation=(
                f"{len(errors)} errors, "
                f"{len(warnings)} warnings"
            ),
        )
