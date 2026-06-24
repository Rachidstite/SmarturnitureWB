from dataclasses import dataclass


@dataclass
class FactoryDeliveryReport:
    delivery_status: str = "ON_TRACK"
    delivery_confidence: str = "HIGH"
    delivery_recommendation: str = ""
