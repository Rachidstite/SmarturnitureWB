from validation.intelligence.rule_result import (
    RuleResult,
)


class StructuralWarningClassifier:

    STRUCTURAL_CODES = {
        "SHELF_SAG",
        "DIVIDER_RECOMMENDED",
        "BACK_PANEL_REQUIRED",
    }

    @classmethod
    def classify(
        cls,
        results
    ):

        grouped = {}

        for r in results:

            code = getattr(
                r,
                "code",
                None
            )

            if code not in cls.STRUCTURAL_CODES:
                continue

            if code not in grouped:

                grouped[code] = {
                    "result": r,
                    "count": 1,
                }

            else:

                grouped[code]["count"] += 1

        aggregated = []

        for code, data in grouped.items():

            original = data["result"]
            count = data["count"]

            aggregated.append(
                RuleResult(
                    passed=original.passed,
                    level=original.level,
                    code=original.code,
                    message=(
                        f"{original.message} "
                        f"(affected panels: {count})"
                    )
                )
            )

        return aggregated
