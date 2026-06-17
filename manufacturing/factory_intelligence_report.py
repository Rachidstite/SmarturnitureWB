from dataclasses import dataclass


@dataclass
class FactoryIntelligenceReport:
    factory_resource_report: object = None
    factory_capacity_report: object = None
    factory_load_report: object = None
