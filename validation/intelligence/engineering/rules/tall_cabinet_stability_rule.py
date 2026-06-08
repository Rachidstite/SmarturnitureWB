from validation.intelligence.engineering.engineering_result import (
    EngineeringResult,
)

from validation.intelligence.engineering.engineering_level import (
    EngineeringLevel,
)

from shared.roles import NodeRole


class TallCabinetStabilityRule:

    def validate(
        self,
        scene_graph,
    ):

        nodes = getattr(
            scene_graph,
            "physical_nodes",
            []
        )

        side_panels = [
            n
            for n in nodes
            if getattr(
                n,
                "role",
                None
            ) == NodeRole.SIDE_PANEL
        ]

        if not side_panels:
            return EngineeringResult(
                passed=True,
                level=EngineeringLevel.INFO,
                code="NO_CABINET",
                message="No cabinet detected",
            )

        cabinet_height = max(
            getattr(
                p,
                "height",
                0
            )
            for p in side_panels
        )

        has_back_panel = any(
            getattr(
                n,
                "role",
                None
            ) == NodeRole.BACK_PANEL
            for n in nodes
        )

        if (
            cabinet_height > 2600
            and not has_back_panel
        ):
            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.ERROR,
                code="TALL_CABINET_STABILITY",
                message="Tall cabinet requires back panel",
            )

        if (
            cabinet_height > 2200
            and not has_back_panel
        ):
            return EngineeringResult(
                passed=False,
                level=EngineeringLevel.WARNING,
                code="TALL_CABINET_STABILITY",
                message="Tall cabinet may require back panel",
            )

        return EngineeringResult(
            passed=True,
            level=EngineeringLevel.INFO,
            code="OK",
            message="Cabinet stability acceptable",
        )
