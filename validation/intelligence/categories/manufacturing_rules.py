from validation.intelligence.through_hole_thickness_rule import (
    ThroughHoleThicknessRule,
)

from validation.intelligence.unused_operation_rule import (
    UnusedOperationRule,
)


def get_manufacturing_rules():

    return [
        ThroughHoleThicknessRule(),
        UnusedOperationRule(),
    ]
