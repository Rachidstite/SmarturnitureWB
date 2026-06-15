from dataclasses import dataclass, field


@dataclass
class QuotationIntelligenceReport:
    risk_level: str = "UNKNOWN"
    margin_status: str = "UNKNOWN"
    recommendations: list = field(default_factory=list)
