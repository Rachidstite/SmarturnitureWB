from validation.intelligence.rules_registry import (
    RulesRegistry,
)

from validation.intelligence.result_level import (
    ResultLevel,
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

    def errors(
        self,
        results
    ):
        return [
            r for r in results
            if r.level == ResultLevel.ERROR
        ]

    def warnings(
        self,
        results
    ):
        return [
            r for r in results
            if r.level == ResultLevel.WARNING
        ]

    def recommendations(
        self,
        results
    ):
        return [
            r for r in results
            if r.level == ResultLevel.RECOMMENDATION
        ]

    def optimizations(
        self,
        results
    ):
        return [
            r for r in results
            if r.level == ResultLevel.OPTIMIZATION
        ]

    def infos(
        self,
        results
    ):
        return [
            r for r in results
            if r.level == ResultLevel.INFO
        ]


    def has_blocking_errors(
        self,
        results
    ):
        return len(
            self.errors(results)
        ) > 0

    def can_export(
        self,
        results
    ):
        return not self.has_blocking_errors(
            results
        )

    def summary(
        self,
        results
    ):
        return {
            "errors": len(
                self.errors(results)
            ),
            "warnings": len(
                self.warnings(results)
            ),
            "recommendations": len(
                self.recommendations(results)
            ),
            "optimizations": len(
                self.optimizations(results)
            ),
            "infos": len(
                self.infos(results)
            ),
        }
