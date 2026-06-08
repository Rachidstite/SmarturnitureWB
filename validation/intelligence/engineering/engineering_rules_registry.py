class EngineeringRulesRegistry:

    @staticmethod
    def get_rules():

        from validation.intelligence.engineering.rules.shelf_deflection_rule import (
            ShelfDeflectionRule,
        )

        return [
            ShelfDeflectionRule(),
        ]
