from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class WallMountLoadRule:
    rule_id: object | None = None
    business_reason: object | None = None
    engineering_reason: object | None = None
    manufacturing_impact: object | None = None
    validation_target: object | None = None
    severity: object | None = None
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class WallMountAnchorCompatibilityRule:
    rule_id: object | None = None
    business_reason: object | None = None
    engineering_reason: object | None = None
    manufacturing_impact: object | None = None
    validation_target: object | None = None
    severity: object | None = None
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class WallMountClearanceRule:
    rule_id: object | None = None
    business_reason: object | None = None
    engineering_reason: object | None = None
    manufacturing_impact: object | None = None
    validation_target: object | None = None
    severity: object | None = None
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class WallMountRetentionRule:
    rule_id: object | None = None
    business_reason: object | None = None
    engineering_reason: object | None = None
    manufacturing_impact: object | None = None
    validation_target: object | None = None
    severity: object | None = None
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class WallMountHardwareCompatibilityRule:
    rule_id: object | None = None
    business_reason: object | None = None
    engineering_reason: object | None = None
    manufacturing_impact: object | None = None
    validation_target: object | None = None
    severity: object | None = None
    metadata: dict = field(default_factory=dict)
