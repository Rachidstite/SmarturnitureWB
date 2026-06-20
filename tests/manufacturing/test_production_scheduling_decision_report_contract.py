import inspect
from dataclasses import fields, is_dataclass


def test_production_scheduling_decision_report_contract_exists():
    from manufacturing.production_scheduling_decision_report import (
        ProductionSchedulingDecisionReport,
    )

    assert is_dataclass(ProductionSchedulingDecisionReport)


def test_production_scheduling_decision_report_field_inventory_is_stable():
    from manufacturing.production_scheduling_decision_report import (
        ProductionSchedulingDecisionReport,
    )

    assert [field.name for field in fields(ProductionSchedulingDecisionReport)] == [
        "decision_status",
        "is_manufacturable",
        "is_blocked",
        "requires_review",
        "blocking_reason",
        "warning_reason",
        "recommended_fix",
        "production_schedule_action",
        "factory_visibility_message",
    ]


def test_production_scheduling_decision_report_safe_defaults():
    from manufacturing.production_scheduling_decision_report import (
        ProductionSchedulingDecisionReport,
    )

    report = ProductionSchedulingDecisionReport()

    assert report.decision_status == ""
    assert report.is_manufacturable is False
    assert report.is_blocked is False
    assert report.requires_review is False
    assert report.blocking_reason == ""
    assert report.warning_reason == ""
    assert report.recommended_fix == ""
    assert report.production_schedule_action == ""
    assert report.factory_visibility_message == ""


def test_production_scheduling_decision_report_has_no_runtime_or_builder_logic():
    import manufacturing.production_scheduling_decision_report as module

    source = inspect.getsource(module)

    assert "for " not in source
    assert "while " not in source
    assert "append(" not in source
    assert "build(" not in source
    assert "builder" not in source.lower()
    assert "intelligence" not in source.lower()
    assert "calculate" not in source.lower()
    assert "schedule_risk" not in source.lower()
    assert "capacity_utilization" not in source.lower()
    assert "runtime" not in source.lower()
    assert "compiler" not in source.lower()
    assert "cnc" not in source.lower()
    assert "geometry" not in source.lower()
    assert "resource" not in source.lower()


def test_production_scheduling_decision_report_does_not_change_runtime_behavior():
    from domain.back_panel_engine import BackPanelEngine, BackPanelRule

    rule = BackPanelRule()

    assert BackPanelEngine.groove_width(rule) == rule.thickness + rule.groove_clearance
    assert BackPanelEngine.insertion_depth(rule) == rule.groove_depth
    assert BackPanelEngine.offset(rule) == rule.groove_offset
