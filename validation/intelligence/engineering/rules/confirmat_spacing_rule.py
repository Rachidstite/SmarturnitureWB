from validation.intelligence.engineering.engineering_result import (
    EngineeringResult,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


class ConfirmatSpacingRule:

    def validate(
        self,
        joint,
    ):

        length = getattr(
            joint,
            "joint_length",
            0,
        )

        if length < 700:

            return EngineeringResult(
                passed=True,
                level=EngineeringLevel.INFO,
                code="CONFIRMAT_OK",
                message="Confirmat spacing acceptable",
            )

        if length < 1200:

            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.WARNING,
                code="CONFIRMAT_WARNING",
                message="Additional confirmat screws recommended",
            )

        return EngineeringResult(
            passed=False,
            level=EngineeringLevel.ERROR,
            code="CONFIRMAT_ERROR",
            message="Joint requires additional fastening points",
        )
