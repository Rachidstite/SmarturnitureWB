import inspect
import re

from project_engineering.operational_capability_satisfied_rule import (
    evaluate_operational_capability_satisfied,
)


def test_satisfied_capability_returns_passed_info_with_empty_message():
    result = evaluate_operational_capability_satisfied(
        component_id="cabinet-1",
        capability="operational_clearance",
        is_satisfied=True,
    )

    assert result.passed is True
    assert result.severity == "info"
    assert result.message == ""


def test_unsatisfied_capability_returns_error_result():
    result = evaluate_operational_capability_satisfied(
        component_id="cabinet-1",
        capability="operational_clearance",
        is_satisfied=False,
    )

    assert result.passed is False
    assert result.severity == "error"
    assert result.message == "Operational capability is not satisfied"


def test_result_stores_identity_and_source_fields():
    result = evaluate_operational_capability_satisfied(
        component_id="cabinet-42",
        capability="serviceability",
        is_satisfied=False,
        rule_id="RULE-42",
        source="engineering-policy",
    )

    assert result.component_id == "cabinet-42"
    assert result.capability == "serviceability"
    assert result.rule_id == "RULE-42"
    assert result.source == "engineering-policy"


def test_function_signature_stays_generic():
    signature = inspect.signature(evaluate_operational_capability_satisfied)
    parameters = list(signature.parameters)

    assert parameters == [
        "component_id",
        "capability",
        "is_satisfied",
        "rule_id",
        "source",
    ]
    assert "door" not in signature.parameters
    assert "drawer" not in signature.parameters
    assert "hinge" not in signature.parameters
    assert "slide" not in signature.parameters
    assert "shelf" not in signature.parameters
    assert "panel" not in signature.parameters


def test_module_imports_without_freecad():
    import project_engineering.operational_capability_satisfied_rule as module

    assert module.evaluate_operational_capability_satisfied is evaluate_operational_capability_satisfied


def test_module_has_only_allowed_project_engineering_import():
    import project_engineering.operational_capability_satisfied_rule as module

    source = inspect.getsource(module)

    assert "from project_engineering.operational_rule_result import OperationalRuleResult" in source
    for banned in [
        "project_engineering.operational_decision_report",
        "project_engineering.operational_capability_contract",
        "project_engineering.operational_clearance_contract",
        "project_engineering.motion_contract",
        "project_engineering.accessibility_contract",
        "project_engineering.installation_sequence_contract",
        "project_engineering.serviceability_contract",
        "manufacturing",
        "cost",
        "exports",
        "CNC",
        "FreeCAD",
    ]:
        assert banned not in source

    assert re.search(r"\bui\b", source, flags=re.IGNORECASE) is None


def test_rule_is_generic_and_component_agnostic():
    result = evaluate_operational_capability_satisfied(
        component_id="component-x",
        capability="generic_capability",
        is_satisfied=True,
    )

    assert result.rule_id == "OPERATIONAL_CAPABILITY_SATISFIED"
    assert result.component_id == "component-x"
    assert result.capability == "generic_capability"
    assert not any(
        hasattr(result, field)
        for field in [
            "door",
            "drawer",
            "hinge",
            "slide",
            "shelf",
            "panel",
        ]
    )
