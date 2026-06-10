class RecommendationSorter:

    PRIORITY_ORDER = {
        "CRITICAL": 0,
        "HIGH": 1,
        "MEDIUM": 2,
        "LOW": 3,
    }

    def sort(
        self,
        recommendations,
    ):

        return sorted(
            recommendations,
            key=lambda r: (
                self.PRIORITY_ORDER.get(
                    r.priority,
                    999,
                ),
                -getattr(
                    r,
                    "roi_score",
                    0,
                ),
            ),
        )
