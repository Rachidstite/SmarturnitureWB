import inspect

from dataclasses import fields, is_dataclass


def test_minifix_rule_report_contract_exists():
    from manufacturing.minifix_rule_report import MinifixRuleReport

    assert is_dataclass(MinifixRuleReport)


def test_minifix_rule_report_field_inventory_is_stable():
    from manufacturing.minifix_rule_report import MinifixRuleReport

    assert [field.name for field in fields(MinifixRuleReport)] == [
        "minimum_edge_distance",
        "minimum_panel_thickness",
        "minimum_spacing",
        "maximum_spacing",
        "requires_cam_lock",
        "requires_dowel_support",
        "recommended_pattern",
        "recommended_quantity",
    ]


def test_minifix_rule_report_safe_defaults():
    from manufacturing.minifix_rule_report import MinifixRuleReport

    report = MinifixRuleReport()

    assert report.minimum_edge_distance == 0.0
    assert report.minimum_panel_thickness == 0.0
    assert report.minimum_spacing == 0.0
    assert report.maximum_spacing == 0.0
    assert report.requires_cam_lock is False
    assert report.requires_dowel_support is False
    assert report.recommended_pattern == ""
    assert report.recommended_quantity == 0


def test_minifix_rule_report_has_no_rule_evaluation_logic():
    import manufacturing.minifix_rule_report as module

    source = inspect.getsource(module)

    assert "for " not in source
    assert "while " not in source
    assert "append(" not in source
    assert "evaluate" not in source.lower()
    assert "calculate" not in source.lower()
    assert "ManufacturingCompiler" not in source
    assert "FactoryDecisionBuilder" not in source
    assert "ProductionReadinessBuilder" not in source


def test_minifix_rule_report_has_no_geometry_cnc_or_runtime_imports():
    import manufacturing.minifix_rule_report as module

    source = inspect.getsource(module)

    assert "geometry" not in source.lower()
    assert "CNC" not in source
    assert "compiler" not in source.lower()
    assert "runtime" not in source.lower()


def test_minifix_rule_report_does_not_change_runtime_behavior():
    from domain.back_panel_engine import BackPanelEngine, BackPanelRule

    rule = BackPanelRule()

    assert BackPanelEngine.groove_width(rule) == rule.thickness + rule.groove_clearance
    assert BackPanelEngine.insertion_depth(rule) == rule.groove_depth
    assert BackPanelEngine.offset(rule) == rule.groove_offset
