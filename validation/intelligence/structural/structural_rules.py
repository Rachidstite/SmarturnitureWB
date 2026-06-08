from validation.intelligence.structural.shelf_sag_rule import (
    ShelfSagRule,
)

from validation.intelligence.structural.divider_spacing_rule import (
    DividerSpacingRule,
)

from validation.intelligence.structural.back_panel_required_rule import (
    BackPanelRequiredRule,
)

from validation.intelligence.structural.door_hinge_recommendation_rule import (
    DoorHingeRecommendationRule,
)


def get_structural_rules():

    return [
        ShelfSagRule(),
        DividerSpacingRule(),
        BackPanelRequiredRule(),
        DoorHingeRecommendationRule(),
    ]
