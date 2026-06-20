import inspect

from dataclasses import fields, is_dataclass


def test_confirmat_validation_report_contract_exists():
    from manufacturing.confirmat_validation_report import ConfirmatValidationReport

    assert is_dataclass(ConfirmatValidationReport)


def test_confirmat_validation_report_field_inventory_is_stable():
    from manufacturing.confirmat_validation_report import ConfirmatValidationReport

    assert [field.name for field in fields(ConfirmatValidationReport)] == [
        "validation_status",
        "is_valid",
        "edge_distance_risk",
        "spacing_risk",
        "assembly_risk",
        "manufacturing_warning",
        "recommended_action",
    ]


def test_confirmat_validation_report_safe_defaults():
    from manufacturing.confirmat_validation_report import ConfirmatValidationReport

    report = ConfirmatValidationReport()

    assert report.validation_status == ""
    assert report.is_valid is False
    assert report.edge_distance_risk == ""
    assert report.spacing_risk == ""
    assert report.assembly_risk == ""
    assert report.manufacturing_warning == ""
    assert report.recommended_action == ""


def test_confirmat_validation_report_has_no_validation_or_placement_logic():
    import manufacturing.confirmat_validation_report as module

    source = inspect.getsource(module)

    assert "for " not in source
    assert "while " not in source
    assert "append(" not in source
    assert "validate" not in source.lower()
    assert "evaluate" not in source.lower()
    assert "calculate" not in source.lower()
    assert "placement" not in source.lower()
    assert "hole" not in source.lower()
    assert "ManufacturingCompiler" not in source
    assert "FactoryDecisionBuilder" not in source
    assert "ProductionReadinessBuilder" not in source


def test_confirmat_validation_report_has_no_cnc_runtime_or_compiler_imports():
    import manufacturing.confirmat_validation_report as module

    source = inspect.getsource(module)

    assert "CNC" not in source
    assert "runtime" not in source.lower()
    assert "compiler" not in source.lower()
    assert "geometry" not in source.lower()


def test_confirmat_validation_report_does_not_change_runtime_behavior():
    from domain.back_panel_engine import BackPanelEngine, BackPanelRule

    rule = BackPanelRule()

    assert BackPanelEngine.groove_width(rule) == rule.thickness + rule.groove_clearance
    assert BackPanelEngine.insertion_depth(rule) == rule.groove_depth
    assert BackPanelEngine.offset(rule) == rule.groove_offset
