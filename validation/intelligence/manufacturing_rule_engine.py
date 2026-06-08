from validation.intelligence.panel_rules_registry import (
    PanelRulesRegistry,
)

from validation.intelligence.operation_rules_registry import (
    OperationRulesRegistry,
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

        panel_rules = (
            PanelRulesRegistry.get_rules()
        )

        operation_rules = (
            OperationRulesRegistry.get_rules()
        )

        for panel in panel_specs:

            # PASS 1 : PANEL RULES

            for rule in panel_rules:

                try:

                    result = rule.validate(
                        panel,
                        None
                    )

                    results.append(result)

                except (
                    AttributeError,
                    KeyError,
                ):
                    pass

            # PASS 2 : OPERATION RULES

            for op in getattr(
                panel,
                "unified_operations",
                []
            ):

                for rule in operation_rules:

                    result = rule.validate(
                        panel,
                        op
                    )

                    results.append(result)

        return results

    def errors(self, results):
        return [
            r for r in results
            if r.level == ResultLevel.ERROR
        ]

    def warnings(self, results):
        return [
            r for r in results
            if r.level == ResultLevel.WARNING
        ]

    def recommendations(self, results):
        return [
            r for r in results
            if r.level == ResultLevel.RECOMMENDATION
        ]

    def optimizations(self, results):
        return [
            r for r in results
            if r.level == ResultLevel.OPTIMIZATION
        ]

    def infos(self, results):
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
            "errors": len(self.errors(results)),
            "warnings": len(self.warnings(results)),
            "recommendations": len(self.recommendations(results)),
            "optimizations": len(self.optimizations(results)),
            "infos": len(self.infos(results)),
        }
