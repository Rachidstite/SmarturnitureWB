from validation.intelligence.engineering.engineering_result import (
    EngineeringResult,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


class UpperCabinetSpanRule:

    def validate(
        self,
        cabinet,
    ):

        if getattr(
            cabinet,
            "cabinet_type",
            "",
        ) != "upper_cabinet":
            return EngineeringResult(
                passed=True,
                level=EngineeringLevel.INFO,
                code="NOT_UPPER_CABINET",
                message="Not an upper cabinet",
            )

        width = getattr(
            cabinet,
            "width",
            0,
        )

        if width >= 1600:
            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.ERROR,
                code="UPPER_CABINET_SPAN",
                message="Upper cabinet span excessive",
            )

        if width >= 1200:
            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.WARNING,
                code="UPPER_CABINET_SPAN",
                message="Upper cabinet may require reinforcement",
            )

        return EngineeringResult(
            passed=True,
            level=EngineeringLevel.INFO,
            code="OK",
            message="Upper cabinet span acceptable",
        )
