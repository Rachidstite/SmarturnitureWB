import inspect

from dataclasses import MISSING, fields, is_dataclass


def test_minifix_intelligence_report_exists():
    from manufacturing.minifix_intelligence_report import MinifixIntelligenceReport

    assert is_dataclass(MinifixIntelligenceReport)


def test_minifix_intelligence_report_field_inventory_is_stable():
    from manufacturing.minifix_intelligence_report import MinifixIntelligenceReport

    assert [field.name for field in fields(MinifixIntelligenceReport)] == [
        "hardware_sku",
        "placement",
        "pattern",
        "rules",
        "validation",
        "decision",
    ]


def test_minifix_intelligence_report_safe_nested_defaults():
    from manufacturing.minifix_intelligence_report import MinifixIntelligenceReport

    report = MinifixIntelligenceReport()

    assert report.hardware_sku is not None
    assert report.placement is not None
    assert report.pattern is not None
    assert report.rules is not None
    assert report.validation is not None
    assert report.decision is not None


def test_minifix_intelligence_report_uses_existing_minifix_report_types():
    from manufacturing.minifix_decision_report import MinifixDecisionReport
    from manufacturing.minifix_hardware_sku import MinifixHardwareSku
    from manufacturing.minifix_intelligence_report import MinifixIntelligenceReport
    from manufacturing.minifix_pattern_report import MinifixPatternReport
    from manufacturing.minifix_placement_report import MinifixPlacementReport
    from manufacturing.minifix_rule_report import MinifixRuleReport
    from manufacturing.minifix_validation_report import MinifixValidationReport

    fields_by_name = {field.name: field for field in fields(MinifixIntelligenceReport)}

    assert fields_by_name["hardware_sku"].default is MISSING
    assert fields_by_name["placement"].default is MISSING
    assert fields_by_name["pattern"].default is MISSING
    assert fields_by_name["rules"].default is MISSING
    assert fields_by_name["validation"].default is MISSING
    assert fields_by_name["decision"].default is MISSING

    assert fields_by_name["hardware_sku"].default_factory is MinifixHardwareSku
    assert fields_by_name["placement"].default_factory is MinifixPlacementReport
    assert fields_by_name["pattern"].default_factory is MinifixPatternReport
    assert fields_by_name["rules"].default_factory is MinifixRuleReport
    assert fields_by_name["validation"].default_factory is MinifixValidationReport
    assert fields_by_name["decision"].default_factory is MinifixDecisionReport


def test_minifix_intelligence_report_nested_defaults_are_not_shared():
    from manufacturing.minifix_intelligence_report import MinifixIntelligenceReport

    first = MinifixIntelligenceReport()
    second = MinifixIntelligenceReport()

    assert first.hardware_sku is not second.hardware_sku
    assert first.placement is not second.placement
    assert first.pattern is not second.pattern
    assert first.rules is not second.rules
    assert first.validation is not second.validation
    assert first.decision is not second.decision


def test_minifix_intelligence_report_has_no_aggregation_logic():
    import manufacturing.minifix_intelligence_report as module

    source = inspect.getsource(module)

    assert "for " not in source
    assert "while " not in source
    assert "append(" not in source
    assert "aggregate" not in source.lower()
    assert "builder" not in source.lower()
    assert "ManufacturingCompiler" not in source
    assert "FactoryDecisionBuilder" not in source
    assert "ProductionReadinessBuilder" not in source


def test_minifix_intelligence_report_has_no_builder_runtime_or_cost_imports():
    import manufacturing.minifix_intelligence_report as module

    source = inspect.getsource(module)

    assert "builder" not in source.lower()
    assert "runtime" not in source.lower()
    assert "CNC" not in source
    assert "compiler" not in source.lower()
    assert "cost_intelligence" not in source
    assert "quotation" not in source.lower()


def test_minifix_intelligence_report_does_not_change_runtime_behavior():
    from domain.back_panel_engine import BackPanelEngine, BackPanelRule

    rule = BackPanelRule()

    assert BackPanelEngine.groove_width(rule) == rule.thickness + rule.groove_clearance
    assert BackPanelEngine.insertion_depth(rule) == rule.groove_depth
    assert BackPanelEngine.offset(rule) == rule.groove_offset
