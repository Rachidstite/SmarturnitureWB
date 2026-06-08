from collections import defaultdict

from validation.intelligence.rule_result import (
    RuleResult,
)


class ResultAggregator:

    @staticmethod
    def aggregate(results):

        groups = defaultdict(list)

        for r in results:

            if r.passed:
                continue

            groups[r.code].append(r)

        aggregated = []

        for code, items in groups.items():

            first = items[0]

            if len(items) == 1:

                aggregated.append(first)
                continue

            aggregated.append(
                RuleResult(
                    passed=False,
                    level=first.level,
                    code=first.code,
                    message=(
                        f"{first.message} "
                        f"(affected panels: {len(items)})"
                    )
                )
            )

        return aggregated
