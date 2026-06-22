from dataclasses import dataclass, field


@dataclass
class HardwareUsageReport:
    hardware_sku_counts: dict = field(default_factory=dict)
    hardware_family_counts: dict = field(default_factory=dict)
    hardware_intent_counts: dict = field(default_factory=dict)
