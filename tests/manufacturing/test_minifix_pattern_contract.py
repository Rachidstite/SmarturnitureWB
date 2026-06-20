import inspect

from dataclasses import fields, is_dataclass


def test_minifix_pattern_report_contract_exists():
    from manufacturing.minifix_pattern_report import MinifixPatternReport

    assert is_dataclass(MinifixPatternReport)


def test_minifix_pattern_report_field_inventory_is_stable():
    from manufacturing.minifix_pattern_report import MinifixPatternReport

    assert [field.name for field in fields(MinifixPatternReport)] == [
        "pattern_type",
        "minifix_count",
        "horizontal_count",
        "vertical_count",
        "corner_count",
        "center_count",
        "symmetrical_pattern",
        "pattern_description",
    ]


def test_minifix_pattern_report_safe_defaults():
    from manufacturing.minifix_pattern_report import MinifixPatternReport

    report = MinifixPatternReport()

    assert report.pattern_type == ""
    assert report.minifix_count == 0
    assert report.horizontal_count == 0
    assert report.vertical_count == 0
    assert report.corner_count == 0
    assert report.center_count == 0
    assert report.symmetrical_pattern is False
    assert report.pattern_description == ""


def test_minifix_pattern_report_has_no_pattern_generation_logic():
    import manufacturing.minifix_pattern_report as module

    source = inspect.getsource(module)

    assert "for " not in source
    assert "while " not in source
    assert "append(" not in source
    assert "calculate" not in source.lower()
    assert "geometry" not in source.lower()
    assert "ManufacturingCompiler" not in source
    assert "FactoryDecisionBuilder" not in source
    assert "ProductionReadinessBuilder" not in source


def test_minifix_pattern_report_has_no_cnc_or_runtime_imports():
    import manufacturing.minifix_pattern_report as module

    source = inspect.getsource(module)

    assert "CNC" not in source
    assert "compiler" not in source.lower()
    assert "runtime" not in source.lower()


def test_minifix_pattern_report_does_not_change_runtime_behavior():
    from domain.back_panel_engine import BackPanelEngine, BackPanelRule

    rule = BackPanelRule()

    assert BackPanelEngine.groove_width(rule) == rule.thickness + rule.groove_clearance
    assert BackPanelEngine.insertion_depth(rule) == rule.groove_depth
    assert BackPanelEngine.offset(rule) == rule.groove_offset
