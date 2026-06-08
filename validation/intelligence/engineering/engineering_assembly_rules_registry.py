class EngineeringAssemblyRulesRegistry:

    @staticmethod
    def get_rules():

        from validation.intelligence.engineering.rules.tall_cabinet_stability_rule import (
            TallCabinetStabilityRule,
        )

        from validation.intelligence.engineering.rules.carcass_rigidity_rule import (
            CarcassRigidityRule,
        )

        return [
            TallCabinetStabilityRule(),
            CarcassRigidityRule(),
        ]
