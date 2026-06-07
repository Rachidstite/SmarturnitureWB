from validation.intelligence.drill_inside_panel_rule import (
    DrillInsidePanelRule,
)

from validation.intelligence.minimum_edge_distance_rule import (
    MinimumEdgeDistanceRule,
)


class RulesRegistry:

    @staticmethod
    def get_rules():

        return [
            DrillInsidePanelRule(),
            MinimumEdgeDistanceRule(),
        ]
