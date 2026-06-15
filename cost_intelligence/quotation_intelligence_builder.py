from cost_intelligence.quotation_intelligence_report import (
    QuotationIntelligenceReport,
)


class QuotationIntelligenceBuilder:

    def build(self, quotation_report, profitability_report):
        gross_margin_rate = profitability_report.gross_margin_rate

        if gross_margin_rate < 0.15:
            return QuotationIntelligenceReport(
                risk_level="HIGH",
                margin_status="LOW_MARGIN",
                recommendations=["Increase selling price."],
            )

        if gross_margin_rate < 0.25:
            return QuotationIntelligenceReport(
                risk_level="MEDIUM",
                margin_status="ACCEPTABLE_MARGIN",
                recommendations=["Review quote before approval."],
            )

        return QuotationIntelligenceReport(
            risk_level="LOW",
            margin_status="HEALTHY_MARGIN",
            recommendations=["Healthy quotation."],
        )
