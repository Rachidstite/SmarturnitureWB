from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class WallMountCapabilitySpecification:
    mounting_type: object | None = None
    wall_type: object | None = None
    suspension_hardware_family: object | None = None
    required_clearance_mm: object | None = None
    max_load_kg: object | None = None
    installation_method: object | None = None


@dataclass(frozen=True)
class WallMountCapabilityValidation:
    is_mounting_supported: object | None = None
    is_load_within_limit: object | None = None
    has_required_clearance: object | None = None
    diagnostics: tuple = field(default_factory=tuple)
    warnings: tuple = field(default_factory=tuple)


@dataclass(frozen=True)
class WallMountCapabilityResult:
    specification: WallMountCapabilitySpecification | None = None
    validation: WallMountCapabilityValidation | None = None
    suspension_hardware: object | None = None
    load_constraints: object | None = None
    clearance_summary: object | None = None
    diagnostics: tuple = field(default_factory=tuple)
    metadata: dict = field(default_factory=dict)
