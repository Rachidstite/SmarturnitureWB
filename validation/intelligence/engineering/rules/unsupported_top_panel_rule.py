from validation.intelligence.engineering.engineering_result import (
    EngineeringResult,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)


class UnsupportedTopPanelRule:

    def validate(
        self,
        panel_spec,
    ):

        if getattr(
            panel_spec,
            "panel_category",
            "",
        ) != "top_panel":
            return EngineeringResult(
                passed=True,
                level=EngineeringLevel.INFO,
                code="NOT_APPLICABLE",
                message="Not a top panel",
            )

        span = getattr(
            panel_spec,
            "span",
            0,
        )

        if span >= 1800:
            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.ERROR,
                code="UNSUPPORTED_TOP_PANEL",
                message="Top panel requires divider or support",
            )

        if span >= 1400:
            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.WARNING,
                code="UNSUPPORTED_TOP_PANEL",
                message="Top panel may require divider support",
            )

        return EngineeringResult(
            passed=True,
            level=EngineeringLevel.INFO,
            code="OK",
            message="Top panel support acceptable",
        )
