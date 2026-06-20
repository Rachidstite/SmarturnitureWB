import inspect

from dataclasses import fields, is_dataclass


def test_minifix_validation_report_contract_exists():
    from manufacturing.minifix_validation_report import MinifixValidationReport

    assert is_dataclass(MinifixValidationReport)


def test_minifix_validation_report_field_inventory_is_stable():
    from manufacturing.minifix_validation_report import MinifixValidationReport

    assert [field.name for field in fields(MinifixValidationReport)] == [
        "is_valid",
        "validation_status",
        "edge_distance_risk",
        "panel_thickness_risk",
        "spacing_risk",
        "cam_lock_risk",
        "dowel_support_risk",
        "assembly_risk",
        "manufacturing_warning",
        "recommended_action",
    ]


def test_minifix_validation_report_safe_defaults():
    from manufacturing.minifix_validation_report import MinifixValidationReport

    report = MinifixValidationReport()

    assert report.is_valid is False
    assert report.validation_status == ""
    assert report.edge_distance_risk == ""
    assert report.panel_thickness_risk == ""
    assert report.spacing_risk == ""
    assert report.cam_lock_risk == ""
    assert report.dowel_support_risk == ""
    assert report.assembly_risk == ""
    assert report.manufacturing_warning == ""
    assert report.recommended_action == ""


def test_minifix_validation_report_has_no_validation_or_evaluation_logic():
    import manufacturing.minifix_validation_report as module

    source = inspect.getsource(module)

    assert "for " not in source
    assert "while " not in source
    assert "append(" not in source
    assert "evaluate" not in source.lower()
    assert "calculate" not in source.lower()
    assert "ManufacturingCompiler" not in source
    assert "FactoryDecisionBuilder" not in source
    assert "ProductionReadinessBuilder" not in source


def test_minifix_validation_report_has_no_geometry_cnc_or_runtime_imports():
    import manufacturing.minifix_validation_report as module

    source = inspect.getsource(module)

    assert "geometry" not in source.lower()
    assert "CNC" not in source
    assert "compiler" not in source.lower()
    assert "runtime" not in source.lower()


def test_minifix_validation_report_does_not_change_runtime_behavior():
    from domain.back_panel_engine import BackPanelEngine, BackPanelRule

    rule = BackPanelRule()

    assert BackPanelEngine.groove_width(rule) == rule.thickness + rule.groove_clearance
    assert BackPanelEngine.insertion_depth(rule) == rule.groove_depth
    assert BackPanelEngine.offset(rule) == rule.groove_offset
