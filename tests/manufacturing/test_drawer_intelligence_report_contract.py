import inspect

from dataclasses import fields, is_dataclass


def test_drawer_intelligence_report_contract_exists():
    from manufacturing.drawer_intelligence_report import DrawerIntelligenceReport

    assert is_dataclass(DrawerIntelligenceReport)


def test_drawer_intelligence_report_field_inventory_is_stable():
    from manufacturing.drawer_intelligence_report import DrawerIntelligenceReport

    assert [field.name for field in fields(DrawerIntelligenceReport)] == [
        "validation",
        "decision",
    ]


def test_drawer_intelligence_report_uses_existing_drawer_report_types():
    from manufacturing.drawer_decision_report import DrawerDecisionReport
    from manufacturing.drawer_intelligence_report import DrawerIntelligenceReport
    from manufacturing.drawer_validation_report import DrawerValidationReport

    fields_by_name = {field.name: field for field in fields(DrawerIntelligenceReport)}

    assert fields_by_name["validation"].default_factory is DrawerValidationReport
    assert fields_by_name["decision"].default_factory is DrawerDecisionReport


def test_drawer_intelligence_report_safe_nested_defaults():
    from manufacturing.drawer_intelligence_report import DrawerIntelligenceReport

    report = DrawerIntelligenceReport()

    assert report.validation is not None
    assert report.decision is not None


def test_drawer_intelligence_report_nested_defaults_are_not_shared():
    from manufacturing.drawer_intelligence_report import DrawerIntelligenceReport

    first = DrawerIntelligenceReport()
    second = DrawerIntelligenceReport()

    assert first.validation is not second.validation
    assert first.decision is not second.decision


def test_drawer_intelligence_report_has_no_runtime_or_geometry_logic():
    import manufacturing.drawer_intelligence_report as module

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


