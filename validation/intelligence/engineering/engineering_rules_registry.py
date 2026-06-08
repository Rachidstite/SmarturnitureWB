class EngineeringRulesRegistry:

    @staticmethod
    def get_rules():

        from validation.intelligence.engineering.rules.shelf_deflection_rule import (
            ShelfDeflectionRule,
        )

        from validation.intelligence.engineering.rules.divider_buckling_rule import (
            DividerBucklingRule,
        )

        return [
            ShelfDeflectionRule(),
            DividerBucklingRule(),
        ]
