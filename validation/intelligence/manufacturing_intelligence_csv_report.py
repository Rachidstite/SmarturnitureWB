class ManufacturingIntelligenceCSVReport:

    def build(
        self,
        report
    ):

        return [
            [
                "Manufacturing Score",
                report.score.score
            ],
            [
                "Grade",
                report.score.grade
            ],
            [
                "Warnings",
                len(report.warnings)
            ],
            [
                "Recommendations",
                len(report.recommendations)
            ],
            [
                "Cost Impacts",
                len(report.cost_impacts)
            ],
            [
                "Can Export",
                report.can_export
            ],
        ]
