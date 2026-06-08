class RecommendationPriority:

    PRIORITIES = {

        "EDGE_ERROR": "CRITICAL",

        "CABINET_OVERTURN": "CRITICAL",

        "ANCHOR_REQUIRED": "HIGH",

        "SHELF_DEFLECTION": "MEDIUM",

        "VERTICAL_SHELF_SUPPORT": "MEDIUM",

        "SHELF_LOAD_CAPACITY": "MEDIUM",
    }

    @classmethod
    def for_code(
        cls,
        code,
    ):
        return cls.PRIORITIES.get(
            code,
            "LOW",
        )
