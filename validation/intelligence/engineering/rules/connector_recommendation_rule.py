from validation.intelligence.engineering.engineering_result import (
    EngineeringResult,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


class ConnectorRecommendationRule:

    def validate(
        self,
        joint,
    ):

        length = getattr(
            joint,
            "joint_length",
            0,
        )

        if length >= 1400:

            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.ERROR,
                code="CONNECTOR_HEAVY_DUTY",
                message="Heavy-duty connector recommended",
            )

        if length >= 700:

            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.WARNING,
                code="CONNECTOR_RECOMMENDED",
                message="Additional connector recommended",
            )

        return EngineeringResult(
            passed=True,
            level=EngineeringLevel.INFO,
            code="CONNECTOR_OK",
            message="Connector recommendation available",
        )
