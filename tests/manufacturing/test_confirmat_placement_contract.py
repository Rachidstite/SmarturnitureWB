import inspect

from dataclasses import fields, is_dataclass


def test_confirmat_placement_report_contract_exists():
    from manufacturing.confirmat_placement_report import ConfirmatPlacementReport

    assert is_dataclass(ConfirmatPlacementReport)


def test_confirmat_placement_report_field_inventory_is_stable():
    from manufacturing.confirmat_placement_report import ConfirmatPlacementReport

    assert [field.name for field in fields(ConfirmatPlacementReport)] == [
        "host_panel_id",
        "target_panel_id",
        "x_position",
        "y_position",
        "z_position",
        "face",
        "axis",
        "placement_type",
    ]


def test_confirmat_placement_report_safe_defaults():
    from manufacturing.confirmat_placement_report import ConfirmatPlacementReport

    report = ConfirmatPlacementReport()

    assert report.host_panel_id == ""
    assert report.target_panel_id == ""
    assert report.x_position == 0.0
    assert report.y_position == 0.0
    assert report.z_position == 0.0
    assert report.face == ""
    assert report.axis == ""
    assert report.placement_type == ""


def test_confirmat_placement_report_has_no_placement_or_geometry_logic():
    import manufacturing.confirmat_placement_report as module

    source = inspect.getsource(module)

    assert "for " not in source
    assert "while " not in source
    assert "append(" not in source
    assert "calculate" not in source.lower()
    assert "generate" not in source.lower()
    assert "geometry" not in source.lower()
    assert "hole" not in source.lower()
    assert "ManufacturingCompiler" not in source
    assert "FactoryDecisionBuilder" not in source
    assert "ProductionReadinessBuilder" not in source


def test_confirmat_placement_report_has_no_cnc_runtime_or_compiler_imports():
    import manufacturing.confirmat_placement_report as module

    source = inspect.getsource(module)

    assert "CNC" not in source
    assert "runtime" not in source.lower()
    assert "compiler" not in source.lower()


def test_confirmat_placement_report_does_not_change_runtime_behavior():
    from domain.back_panel_engine import BackPanelEngine, BackPanelRule

    rule = BackPanelRule()

    assert BackPanelEngine.groove_width(rule) == rule.thickness + rule.groove_clearance
    assert BackPanelEngine.insertion_depth(rule) == rule.groove_depth
    assert BackPanelEngine.offset(rule) == rule.groove_offset
