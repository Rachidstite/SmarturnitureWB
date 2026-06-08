from validation.intelligence.categories.geometric_rules import (
    get_geometric_rules,
)

from validation.intelligence.categories.hardware_rules import (
    get_hardware_rules,
)

from validation.intelligence.categories.manufacturing_rules import (
    get_manufacturing_rules,
)


class OperationRulesRegistry:

    @staticmethod
    def get_rules():

        return (
            get_geometric_rules()
            + get_hardware_rules()
            + get_manufacturing_rules()
        )
