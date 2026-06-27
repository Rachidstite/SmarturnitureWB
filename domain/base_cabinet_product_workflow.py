from __future__ import annotations

from domain.base_cabinet_engineering_entry import (
    build_base_cabinet_engineering_cabinet,
)
from domain.base_cabinet_manufacturing_outputs_entry import (
    build_base_cabinet_manufacturing_outputs_entry,
)
from domain.base_cabinet_product_result import BaseCabinetProductResult
from domain.base_cabinet_scenario import BaseCabinetScenario
from domain.base_cabinet_specification import BaseCabinetSpecification
from domain.base_cabinet_specification_validation import (
    validate_base_cabinet_specification,
)


def build_base_cabinet_product_workflow(
    specification: BaseCabinetSpecification,
) -> BaseCabinetProductResult:
    scenario = BaseCabinetScenario(specification=specification)
    engineering = build_base_cabinet_engineering_cabinet(specification)
    validation = validate_base_cabinet_specification(specification)
    manufacturing_outputs = build_base_cabinet_manufacturing_outputs_entry(
        specification
    )

    return BaseCabinetProductResult(
        specification=specification,
        scenario=scenario,
        engineering=engineering,
        validation=validation,
        manufacturing_outputs=manufacturing_outputs,
        metadata=dict(getattr(manufacturing_outputs, "metadata", {}) or {}),
        diagnostics=tuple(getattr(validation, "violations", ()) or ()),
    )
