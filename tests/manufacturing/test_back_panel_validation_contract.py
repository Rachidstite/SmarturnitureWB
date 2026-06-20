import inspect

from dataclasses import fields, is_dataclass


def test_back_panel_validation_report_exists():
    from manufacturing.back_panel_validation_report import (
        BackPanelValidationReport,
    )

    assert is_dataclass(BackPanelValidationReport)


def test_back_panel_validation_report_field_inventory_is_stable():
    from manufacturing.back_panel_validation_report import (
        BackPanelValidationReport,
    )

    assert [field.name for field in fields(BackPanelValidationReport)] == [
        "is_valid",
        "validation_status",
        "width_risk",
        "height_risk",
        "spacing_risk",
        "edge_risk",
        "corner_risk",
        "center_support_required",
        "center_holes_required",
        "fixing_method_warning",
        "manufacturing_warning",
        "recommended_action",
    ]


def test_back_panel_validation_report_safe_defaults():
    from manufacturing.back_panel_validation_report import (
        BackPanelValidationReport,
    )

    report = BackPanelValidationReport()

    assert report.is_valid is False
    assert report.validation_status == ""
    assert report.width_risk == ""
    assert report.height_risk == ""
    assert report.spacing_risk == ""
    assert report.edge_risk == ""
    assert report.corner_risk == ""
    assert report.center_support_required is False
    assert report.center_holes_required is False
    assert report.fixing_method_warning == ""
    assert report.manufacturing_warning == ""
    assert report.recommended_action == ""


def test_back_panel_validation_report_has_no_validation_logic():
    import manufacturing.back_panel_validation_report as module

    source = inspect.getsource(module)

    assert "for " not in source
    assert "while " not in source
    assert "append(" not in source
    assert "validate(" not in source
    assert "ManufacturingCompiler" not in source
    assert "FactoryDecisionBuilder" not in source
    assert "ProductionReadinessBuilder" not in source


def test_back_panel_validation_report_has_no_cnc_or_runtime_imports():
    import manufacturing.back_panel_validation_report as module

    source = inspect.getsource(module)

    assert "CNC" not in source
    assert "compiler" not in source.lower()
    assert "runtime" not in source.lower()


def test_back_panel_validation_report_does_not_change_runtime_behavior():
    from domain.back_panel_engine import BackPanelEngine, BackPanelRule

    rule = BackPanelRule()

    assert BackPanelEngine.groove_width(rule) == rule.thickness + rule.groove_clearance
    assert BackPanelEngine.insertion_depth(rule) == rule.groove_depth
    assert BackPanelEngine.offset(rule) == rule.groove_offset
