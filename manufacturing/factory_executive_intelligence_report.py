from dataclasses import dataclass


@dataclass
class FactoryExecutiveIntelligenceReport:
    factory_status: str = "STABLE"
    capacity_status: str = "UNKNOWN"
    load_status: str = "LOW"
    main_bottleneck: str = ""
    delivery_confidence: str = "LOW"
    delivery_risk: str = "HIGH"
    priority_action: str = ""
    summary: str = "Factory intelligence available."
