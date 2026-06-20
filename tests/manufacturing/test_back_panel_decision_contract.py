import inspect

from dataclasses import fields, is_dataclass


def test_back_panel_decision_report_exists():
    from manufacturing.back_panel_decision_report import BackPanelDecisionReport

    assert is_dataclass(BackPanelDecisionReport)


def test_back_panel_decision_report_field_inventory_is_stable():
    from manufacturing.back_panel_decision_report import BackPanelDecisionReport

    assert [field.name for field in fields(BackPanelDecisionReport)] == [
        "decision_status",
        "is_manufacturable",
        "is_blocked",
        "requires_review",
        "blocking_reason",
        "warning_reason",
        "recommended_fix",
        "manufacturing_priority",
        "factory_visibility_message",
    ]


def test_back_panel_decision_report_safe_defaults():
    from manufacturing.back_panel_decision_report import BackPanelDecisionReport

    report = BackPanelDecisionReport()

    assert report.decision_status == ""
    assert report.is_manufacturable is False
    assert report.is_blocked is False
    assert report.requires_review is False
    assert report.blocking_reason == ""
    assert report.warning_reason == ""
    assert report.recommended_fix == ""
    assert report.manufacturing_priority == ""
    assert report.factory_visibility_message == ""


def test_back_panel_decision_report_has_no_decision_engine_logic():
    import manufacturing.back_panel_decision_report as module

    source = inspect.getsource(module)

    assert "for " not in source
    assert "while " not in source
    assert "append(" not in source
    assert "decision_engine" not in source.lower()
    assert "validate(" not in source
    assert "ManufacturingCompiler" not in source
    assert "FactoryDecisionBuilder" not in source
    assert "ProductionReadinessBuilder" not in source


def test_back_panel_decision_report_has_no_validation_or_generation_logic():
    import manufacturing.back_panel_decision_report as module

    source = inspect.getsource(module)

    assert "CNC" not in source
    assert "compiler" not in source.lower()
    assert "runtime" not in source.lower()


def test_back_panel_decision_report_does_not_change_runtime_behavior():
    from domain.back_panel_engine import BackPanelEngine, BackPanelRule

    rule = BackPanelRule()

    assert BackPanelEngine.groove_width(rule) == rule.thickness + rule.groove_clearance
    assert BackPanelEngine.insertion_depth(rule) == rule.groove_depth
    assert BackPanelEngine.offset(rule) == rule.groove_offset
