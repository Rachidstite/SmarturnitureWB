class EngineeringRuleEngine:

    def __init__(
        self,
        rules=None,
    ):
        self._rules = rules or []

    def validate(
        self,
        panel_specs,
    ):

        results = []

        for panel in panel_specs:

            for rule in self._rules:

                result = rule.validate(
                    panel
                )

                if result:
                    results.append(
                        result
                    )

        return results
