from __future__ import annotations

from domain.base_cabinet_specification import BaseCabinetSpecification
from domain.base_cabinet_specification_adapter import BaseCabinetSpecificationAdapter
from engine.cabinet import Cabinet

try:
    from engine.cabinet_builder import CabinetBuilder
except Exception:  # pragma: no cover - fallback for contract-only environments
    CabinetBuilder = None


def build_base_cabinet_engineering_cabinet(
    specification: BaseCabinetSpecification,
) -> Cabinet:
    adapter_result = BaseCabinetSpecificationAdapter.adapt(specification)
    cabinet = Cabinet(params=adapter_result.cabinet_params)

    if CabinetBuilder is None:
        raise RuntimeError("CabinetBuilder is unavailable")

    CabinetBuilder().build(cabinet)
    return cabinet
