import inspect

from dataclasses import fields, is_dataclass


def test_back_panel_commercial_risk_report_exists():
    from manufacturing.back_panel_commercial_risk_report import (
        BackPanelCommercialRiskReport,
    )

    assert is_dataclass(BackPanelCommercialRiskReport)


def test_back_panel_commercial_risk_report_field_inventory_is_stable():
    from manufacturing.back_panel_commercial_risk_report import (
        BackPanelCommercialRiskReport,
    )

    assert [field.name for field in fields(BackPanelCommercialRiskReport)] == [
        "risk_level",
        "rework_risk",
        "scrap_risk",
        "labor_delay_risk",
        "cnc_error_risk",
        "customer_complaint_risk",
        "profitability_impact",
        "estimated_waste_category",
        "commercial_warning",
        "recommended_commercial_action",
    ]


def test_back_panel_commercial_risk_report_safe_defaults():
    from manufacturing.back_panel_commercial_risk_report import (
        BackPanelCommercialRiskReport,
    )

    report = BackPanelCommercialRiskReport()

    assert report.risk_level == ""
    assert report.rework_risk == ""
    assert report.scrap_risk == ""
    assert report.labor_delay_risk == ""
    assert report.cnc_error_risk == ""
    assert report.customer_complaint_risk == ""
    assert report.profitability_impact == ""
    assert report.estimated_waste_category == ""
    assert report.commercial_warning == ""
    assert report.recommended_commercial_action == ""


def test_back_panel_commercial_risk_report_has_no_commercial_or_cost_logic():
    import manufacturing.back_panel_commercial_risk_report as module

    source = inspect.getsource(module)

    assert "for " not in source
    assert "while " not in source
    assert "append(" not in source
    assert "validate(" not in source
    assert "cost_intelligence" not in source
    assert "quotation" not in source.lower()
    assert "ManufacturingCompiler" not in source
    assert "FactoryDecisionBuilder" not in source
    assert "ProductionReadinessBuilder" not in source


def test_back_panel_commercial_risk_report_has_no_cnc_or_runtime_imports():
    import manufacturing.back_panel_commercial_risk_report as module

    source = inspect.getsource(module)

    assert "CNC" not in source
    assert "compiler" not in source.lower()
    assert "runtime" not in source.lower()


def test_back_panel_commercial_risk_report_does_not_change_runtime_behavior():
    from domain.back_panel_engine import BackPanelEngine, BackPanelRule

    rule = BackPanelRule()

    assert BackPanelEngine.groove_width(rule) == rule.thickness + rule.groove_clearance
    assert BackPanelEngine.insertion_depth(rule) == rule.groove_depth
    assert BackPanelEngine.offset(rule) == rule.groove_offset
