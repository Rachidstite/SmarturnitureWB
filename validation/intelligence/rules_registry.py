from validation.intelligence.drill_inside_panel_rule import (
    DrillInsidePanelRule,
)

from validation.intelligence.minimum_edge_distance_rule import (
    MinimumEdgeDistanceRule,
)

from validation.intelligence.through_hole_thickness_rule import (
    ThroughHoleThicknessRule,
)

from validation.intelligence.connector_intent_rule import (
    ConnectorIntentRule,
)

from validation.intelligence.minifix_depth_rule import (
    MinifixDepthRule,
)


class RulesRegistry:

    @staticmethod
    def get_rules():

        return [
            DrillInsidePanelRule(),
            MinimumEdgeDistanceRule(),
            ThroughHoleThicknessRule(),
            ConnectorIntentRule(),
            MinifixDepthRule(),
        ]
