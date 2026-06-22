import inspect

from dataclasses import fields, is_dataclass


def test_drawer_decision_report_contract_exists():
    from manufacturing.drawer_decision_report import DrawerDecisionReport

    assert is_dataclass(DrawerDecisionReport)


def test_drawer_decision_report_field_inventory_is_stable():
    from manufacturing.drawer_decision_report import DrawerDecisionReport

    assert [field.name for field in fields(DrawerDecisionReport)] == [
        "decision_status",
        "is_manufacturable",
        "is_blocked",
        "requires_review",
        "blocking_reason",
        "warning_reason",
        "recommended_fix",
        "factory_visibility_message",
    ]


def test_drawer_decision_report_safe_defaults():
    from manufacturing.drawer_decision_report import DrawerDecisionReport

    report = DrawerDecisionReport()

    assert report.decision_status == ""
    assert report.is_manufacturable is False
    assert report.is_blocked is False
    assert report.requires_review is False
    assert report.blocking_reason == ""
    assert report.warning_reason == ""
    assert report.recommended_fix == ""
    assert report.factory_visibility_message == ""


def test_drawer_decision_report_has_no_runtime_or_geometry_logic():
    import manufacturing.drawer_decision_report as module

    source = inspect.getsource(module)

    assert "for " not in source
    assert "while " not in source
    assert "append(" not in source
    assert "geometry" not in source.lower()
    assert "calculate" not in source.lower()
    assert "generate" not in source.lower()
    assert "compiler" not in source.lower()
    assert "runtime" not in source.lower()
    assert "FactoryDecisionBuilder" not in source


