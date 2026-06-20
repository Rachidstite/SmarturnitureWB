import inspect

from dataclasses import fields, is_dataclass


def test_confirmat_decision_report_contract_exists():
    from manufacturing.confirmat_decision_report import ConfirmatDecisionReport

    assert is_dataclass(ConfirmatDecisionReport)


def test_confirmat_decision_report_field_inventory_is_stable():
    from manufacturing.confirmat_decision_report import ConfirmatDecisionReport

    assert [field.name for field in fields(ConfirmatDecisionReport)] == [
        "decision_status",
        "is_manufacturable",
        "is_blocked",
        "requires_review",
        "blocking_reason",
        "warning_reason",
        "recommended_fix",
        "factory_visibility_message",
    ]


def test_confirmat_decision_report_safe_defaults():
    from manufacturing.confirmat_decision_report import ConfirmatDecisionReport

    report = ConfirmatDecisionReport()

    assert report.decision_status == ""
    assert report.is_manufacturable is False
    assert report.is_blocked is False
    assert report.requires_review is False
    assert report.blocking_reason == ""
    assert report.warning_reason == ""
    assert report.recommended_fix == ""
    assert report.factory_visibility_message == ""


def test_confirmat_decision_report_has_no_decision_or_validation_logic():
    import manufacturing.confirmat_decision_report as module

    source = inspect.getsource(module)

    assert "for " not in source
    assert "while " not in source
    assert "append(" not in source
    assert "decide" not in source.lower()
    assert "validate" not in source.lower()
    assert "evaluate" not in source.lower()
    assert "calculate" not in source.lower()
    assert "placement" not in source.lower()
    assert "hole" not in source.lower()
    assert "ManufacturingCompiler" not in source
    assert "FactoryDecisionBuilder" not in source
    assert "ProductionReadinessBuilder" not in source


def test_confirmat_decision_report_has_no_cnc_runtime_or_compiler_imports():
    import manufacturing.confirmat_decision_report as module

    source = inspect.getsource(module)

    assert "CNC" not in source
    assert "runtime" not in source.lower()
    assert "compiler" not in source.lower()
    assert "geometry" not in source.lower()


def test_confirmat_decision_report_does_not_change_runtime_behavior():
    from domain.back_panel_engine import BackPanelEngine, BackPanelRule

    rule = BackPanelRule()

    assert BackPanelEngine.groove_width(rule) == rule.thickness + rule.groove_clearance
    assert BackPanelEngine.insertion_depth(rule) == rule.groove_depth
    assert BackPanelEngine.offset(rule) == rule.groove_offset
