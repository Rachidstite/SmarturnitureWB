from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class BaseCabinetProductResult:
    specification: object | None = None
    scenario: object | None = None
    engineering: object | None = None
    validation: object | None = None
    manufacturing_outputs: object | None = None
    cost: object | None = None
    commercial: object | None = None
    quotation_document: object | None = None
    metadata: dict = field(default_factory=dict)
    diagnostics: tuple = field(default_factory=tuple)
