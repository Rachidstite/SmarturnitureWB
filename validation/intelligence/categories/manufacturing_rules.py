from validation.intelligence.through_hole_thickness_rule import (
    ThroughHoleThicknessRule,
)


def get_manufacturing_rules():

    return [
        ThroughHoleThicknessRule(),
    ]
