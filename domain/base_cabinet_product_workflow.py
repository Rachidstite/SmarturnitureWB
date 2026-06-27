from __future__ import annotations

from types import SimpleNamespace

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
from manufacturing.manufacturing_validation_builder import (
    build_manufacturing_validation_report,
)
from manufacturing.manufacturing_validation_summary_builder import (
    build_manufacturing_validation_summary_report,
)
from services.manufacturing_validation_service import (
    ManufacturingValidationService,
)
from project_engineering.operational_rule_result import OperationalRuleResult


def _scene_graph_from_cabinet(cabinet):
    return getattr(cabinet, "graph", None) or getattr(
        cabinet,
        "scene_graph",
        None,
    )


def _operational_rule_results_from_validation_state(validation_state):
    rule_results = []
    for issue in getattr(validation_state, "issues", []) or []:
        level = str(getattr(issue, "level", "") or "").upper()
        severity = "warning" if level == "WARNING" else "error"
        passed = level not in {"ERROR", "FATAL", "WARNING"}
        component_id = str(
            getattr(issue, "component", None)
            or getattr(issue, "node_id", None)
            or ""
        )
        rule_results.append(
            OperationalRuleResult(
                rule_id=str(getattr(issue, "code", "") or ""),
                capability="manufacturing_validation",
                component_id=component_id,
                passed=passed,
                severity=severity,
                message=str(getattr(issue, "message", "") or ""),
                source="base-cabinet-product-workflow",
            )
        )
    return rule_results


def _build_validation_bridge(
    engineering_validation_report,
    cabinet,
):
    scene_graph = _scene_graph_from_cabinet(cabinet)
    if scene_graph is None:
        raise RuntimeError("Engineering cabinet did not expose a scene graph")

    manufacturing_validation_state = ManufacturingValidationService.validate(
        scene_graph
    )
    manufacturing_rule_results = _operational_rule_results_from_validation_state(
        manufacturing_validation_state
    )
    manufacturing_validation_report = build_manufacturing_validation_report(
        manufacturing_rule_results
    )
    manufacturing_validation_summary_report = (
        build_manufacturing_validation_summary_report(
            manufacturing_validation_report,
            manufacturing_rule_results,
        )
    )

    return SimpleNamespace(
        engineering_validation_report=engineering_validation_report,
        manufacturing_validation_state=manufacturing_validation_state,
        manufacturing_validation_report=manufacturing_validation_report,
        manufacturing_validation_summary_report=manufacturing_validation_summary_report,
        manufacturing_validation_rule_results=tuple(manufacturing_rule_results),
    )


def build_base_cabinet_product_workflow(
    specification: BaseCabinetSpecification,
) -> BaseCabinetProductResult:
    scenario = BaseCabinetScenario(specification=specification)
    engineering = build_base_cabinet_engineering_cabinet(specification)
    engineering_validation = validate_base_cabinet_specification(specification)
    validation = _build_validation_bridge(
        engineering_validation,
        engineering,
    )
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
        diagnostics=tuple(
            getattr(engineering_validation, "violations", ()) or ()
        )
        + tuple(
            getattr(validation.manufacturing_validation_state, "issues", ()) or ()
        ),
    )
