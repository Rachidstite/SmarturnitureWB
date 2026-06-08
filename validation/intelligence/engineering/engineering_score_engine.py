from validation.intelligence.engineering.engineering_score_calculator import (
    EngineeringScoreCalculator,
)


class EngineeringScoreEngine:

    def calculate(
        self,
        report,
    ):

        return (
            EngineeringScoreCalculator()
            .calculate(
                warnings=getattr(
                    report,
                    "warnings",
                    [],
                ),
                errors=getattr(
                    report,
                    "errors",
                    [],
                ),
            )
        )
