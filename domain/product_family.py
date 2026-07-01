from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ProductFamily:
    family_id: str = ""
    name: str = ""
    category: str = ""
    description: str = ""
    default_parameters: dict = field(default_factory=dict)
    engineering_defaults: dict = field(default_factory=dict)
    manufacturing_defaults: dict = field(default_factory=dict)
    visual_defaults: dict = field(default_factory=dict)
    commercial_defaults: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
