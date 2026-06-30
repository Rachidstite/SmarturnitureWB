from dataclasses import dataclass, field


@dataclass
class FactoryReleasePackage:
    manufacturing_decision: object = None
    cut_list: object = None
    hardware_bom: object = None
    cnc_package: object = None
    assembly_package: object = None
    warnings: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
