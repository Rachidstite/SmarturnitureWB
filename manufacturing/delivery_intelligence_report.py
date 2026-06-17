from dataclasses import dataclass


@dataclass
class DeliveryIntelligenceReport:
    estimated_hours: float = 0.0
    estimated_days: float = 0.0
    confidence: str = "LOW"
    delivery_risk: str = "HIGH"
    recommendation: str = "Review delivery plan"
