class EngineeringAssemblyRuleEngine:

    def __init__(
        self,
        rules=None,
    ):
        self._rules = rules or []

    def validate(
        self,
        scene_graph,
    ):

        results = []

        for rule in self._rules:

            result = rule.validate(
                scene_graph
            )

            if result:
                results.append(
                    result
                )

        return results
