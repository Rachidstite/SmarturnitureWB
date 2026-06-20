import inspect

from dataclasses import fields, is_dataclass


def test_minifix_decision_report_contract_exists():
    from manufacturing.minifix_decision_report import MinifixDecisionReport

    assert is_dataclass(MinifixDecisionReport)


def test_minifix_decision_report_field_inventory_is_stable():
    from manufacturing.minifix_decision_report import MinifixDecisionReport

    assert [field.name for field in fields(MinifixDecisionReport)] == [
        "decision_status",
        "is_manufacturable",
        "is_blocked",
        "requires_review",
        "blocking_reason",
        "warning_reason",
        "recommended_fix",
        "assembly_priority",
        "factory_visibility_message",
    ]


def test_minifix_decision_report_safe_defaults():
    from manufacturing.minifix_decision_report import MinifixDecisionReport

    report = MinifixDecisionReport()

    assert report.decision_status == ""
    assert report.is_manufacturable is False
    assert report.is_blocked is False
    assert report.requires_review is False
    assert report.blocking_reason == ""
    assert report.warning_reason == ""
    assert report.recommended_fix == ""
    assert report.assembly_priority == ""
    assert report.factory_visibility_message == ""


def test_minifix_decision_report_has_no_decision_or_evaluation_logic():
    import manufacturing.minifix_decision_report as module

    source = inspect.getsource(module)

    assert "for " not in source
    assert "while " not in source
    assert "append(" not in source
    assert "evaluate" not in source.lower()
    assert "validate" not in source.lower()
    assert "ManufacturingCompiler" not in source
    assert "FactoryDecisionBuilder" not in source
    assert "ProductionReadinessBuilder" not in source


def test_minifix_decision_report_has_no_geometry_cnc_or_runtime_imports():
    import manufacturing.minifix_decision_report as module

    source = inspect.getsource(module)

    assert "geometry" not in source.lower()
    assert "CNC" not in source
    assert "compiler" not in source.lower()
    assert "runtime" not in source.lower()


def test_minifix_decision_report_does_not_change_runtime_behavior():
    from domain.back_panel_engine import BackPanelEngine, BackPanelRule

    rule = BackPanelRule()

    assert BackPanelEngine.groove_width(rule) == rule.thickness + rule.groove_clearance
    assert BackPanelEngine.insertion_depth(rule) == rule.groove_depth
    assert BackPanelEngine.offset(rule) == rule.groove_offset
