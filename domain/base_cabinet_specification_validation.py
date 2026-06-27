from __future__ import annotations

from types import SimpleNamespace

from domain.base_cabinet_specification import BaseCabinetSpecification
from domain.base_cabinet_specification_adapter import BaseCabinetSpecificationAdapter
from domain.constraint_engine import CabinetConstraintValidator
from domain.diagnostics import ValidationReport


def _validation_project_from_adapter_result(adapter_result):
    cabinet_params = adapter_result.cabinet_params

    topology = SimpleNamespace(
        sections={
            0: SimpleNamespace(
                width=cabinet_params.width,
                height=cabinet_params.height,
                depth=cabinet_params.depth,
            )
        }
    )
    graph = SimpleNamespace(
        physical_nodes=[],
        nodes=[],
        _by_role={},
        _by_category={},
    )
    joinery = SimpleNamespace(edges=[])

    return SimpleNamespace(
        params=cabinet_params,
        topology=topology,
        graph=graph,
        joinery=joinery,
        metadata=dict(adapter_result.metadata),
    )


def validate_base_cabinet_specification(
    specification: BaseCabinetSpecification,
) -> ValidationReport:
    adapter_result = BaseCabinetSpecificationAdapter.adapt(specification)
    project = _validation_project_from_adapter_result(adapter_result)
    return CabinetConstraintValidator(project).validate_all()
