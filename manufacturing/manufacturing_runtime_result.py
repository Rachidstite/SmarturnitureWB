from dataclasses import dataclass


@dataclass
class ManufacturingRuntimeResult:
    panel_specs: object
    manufacturing_package: object
    manufacturing_production_package: object
