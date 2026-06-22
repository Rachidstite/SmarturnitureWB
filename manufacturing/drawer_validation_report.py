from dataclasses import dataclass, field


@dataclass
class DrawerValidationReport:
    is_valid: bool = False
    manufacturing_ready: bool = False
    slide_installation_valid: bool = False
    clearance_valid: bool = False
    hardware_complete: bool = False
    blocking_issues: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
