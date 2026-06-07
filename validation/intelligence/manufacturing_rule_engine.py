from validation.intelligence.rules_registry import (
    RulesRegistry,
)


class ManufacturingRuleEngine:

    def validate(
        self,
        panel_specs
    ):

        results = []

        rules = (
            RulesRegistry
            .get_rules()
        )

        for panel in panel_specs:

            for op in getattr(
                panel,
                "unified_operations",
                []
            ):

                for rule in rules:

                    result = (
                        rule.validate(
                            panel,
                            op
                        )
                    )

                    results.append(
                        result
                    )

        return results
