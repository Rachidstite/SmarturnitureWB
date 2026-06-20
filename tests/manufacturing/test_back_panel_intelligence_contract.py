import inspect

from dataclasses import fields, is_dataclass


def test_back_panel_intelligence_report_exists():
    from manufacturing.back_panel_intelligence_report import BackPanelIntelligenceReport

    assert is_dataclass(BackPanelIntelligenceReport)


def test_back_panel_intelligence_report_field_inventory_is_stable():
    from manufacturing.back_panel_intelligence_report import BackPanelIntelligenceReport

    assert [field.name for field in fields(BackPanelIntelligenceReport)] == [
        "hole_rules",
        "manufacturing_intent",
        "validation",
        "decision",
        "commercial_risk",
    ]


def test_back_panel_intelligence_report_safe_nested_defaults():
    from manufacturing.back_panel_commercial_risk_report import (
        BackPanelCommercialRiskReport,
    )
    from manufacturing.back_panel_decision_report import BackPanelDecisionReport
    from manufacturing.back_panel_hole_rule_report import BackPanelHoleRuleReport
    from manufacturing.back_panel_intelligence_report import BackPanelIntelligenceReport
    from manufacturing.back_panel_manufacturing_intent_report import (
        BackPanelManufacturingIntentReport,
    )
    from manufacturing.back_panel_validation_report import BackPanelValidationReport

    report = BackPanelIntelligenceReport()

    assert isinstance(report.hole_rules, BackPanelHoleRuleReport)
    assert isinstance(report.manufacturing_intent, BackPanelManufacturingIntentReport)
    assert isinstance(report.validation, BackPanelValidationReport)
    assert isinstance(report.decision, BackPanelDecisionReport)
    assert isinstance(report.commercial_risk, BackPanelCommercialRiskReport)


def test_back_panel_intelligence_report_uses_existing_nested_types():
    from dataclasses import MISSING

    from manufacturing.back_panel_commercial_risk_report import (
        BackPanelCommercialRiskReport,
    )
    from manufacturing.back_panel_decision_report import BackPanelDecisionReport
    from manufacturing.back_panel_hole_rule_report import BackPanelHoleRuleReport
    from manufacturing.back_panel_intelligence_report import BackPanelIntelligenceReport
    from manufacturing.back_panel_manufacturing_intent_report import (
        BackPanelManufacturingIntentReport,
    )
    from manufacturing.back_panel_validation_report import BackPanelValidationReport

    fields_by_name = {field.name: field for field in fields(BackPanelIntelligenceReport)}

    assert fields_by_name["hole_rules"].default is MISSING
    assert fields_by_name["manufacturing_intent"].default is MISSING
    assert fields_by_name["validation"].default is MISSING
    assert fields_by_name["decision"].default is MISSING
    assert fields_by_name["commercial_risk"].default is MISSING

    assert fields_by_name["hole_rules"].default_factory is BackPanelHoleRuleReport
    assert fields_by_name["manufacturing_intent"].default_factory is BackPanelManufacturingIntentReport
    assert fields_by_name["validation"].default_factory is BackPanelValidationReport
    assert fields_by_name["decision"].default_factory is BackPanelDecisionReport
    assert fields_by_name["commercial_risk"].default_factory is BackPanelCommercialRiskReport


def test_back_panel_intelligence_report_has_no_aggregation_logic():
    import manufacturing.back_panel_intelligence_report as module

    source = inspect.getsource(module)

    assert "for " not in source
    assert "while " not in source
    assert "append(" not in source
    assert "aggregate" not in source.lower()
    assert "ManufacturingCompiler" not in source
    assert "FactoryDecisionBuilder" not in source
    assert "ProductionReadinessBuilder" not in source


def test_back_panel_intelligence_report_has_no_runtime_or_cost_imports():
    import manufacturing.back_panel_intelligence_report as module

    source = inspect.getsource(module)

    assert "CNC" not in source
    assert "compiler" not in source.lower()
    assert "runtime" not in source.lower()
    assert "cost_intelligence" not in source
    assert "quotation" not in source.lower()


def test_back_panel_intelligence_report_does_not_change_runtime_behavior():
    from domain.back_panel_engine import BackPanelEngine, BackPanelRule

    rule = BackPanelRule()

    assert BackPanelEngine.groove_width(rule) == rule.thickness + rule.groove_clearance
    assert BackPanelEngine.insertion_depth(rule) == rule.groove_depth
    assert BackPanelEngine.offset(rule) == rule.groove_offset
