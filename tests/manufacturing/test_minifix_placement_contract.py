import inspect

from dataclasses import fields, is_dataclass


def test_minifix_placement_report_contract_exists():
    from manufacturing.minifix_placement_report import MinifixPlacementReport

    assert is_dataclass(MinifixPlacementReport)


def test_minifix_placement_report_field_inventory_is_stable():
    from manufacturing.minifix_placement_report import MinifixPlacementReport

    assert [field.name for field in fields(MinifixPlacementReport)] == [
        "panel_id",
        "x_position",
        "y_position",
        "z_position",
        "face",
        "cam_position",
        "dowel_position",
        "placement_type",
    ]


def test_minifix_placement_report_safe_defaults():
    from manufacturing.minifix_placement_report import MinifixPlacementReport

    report = MinifixPlacementReport()

    assert report.panel_id == ""
    assert report.x_position == 0.0
    assert report.y_position == 0.0
    assert report.z_position == 0.0
    assert report.face == ""
    assert report.cam_position == ""
    assert report.dowel_position == ""
    assert report.placement_type == ""


def test_minifix_placement_report_has_no_placement_calculations():
    import manufacturing.minifix_placement_report as module

    source = inspect.getsource(module)

    assert "for " not in source
    assert "while " not in source
    assert "append(" not in source
    assert "calculate" not in source.lower()
    assert "geometry" not in source.lower()
    assert "offset(" not in source.lower()
    assert "translate(" not in source.lower()
    assert "ManufacturingCompiler" not in source
    assert "FactoryDecisionBuilder" not in source
    assert "ProductionReadinessBuilder" not in source


def test_minifix_placement_report_has_no_cnc_or_runtime_imports():
    import manufacturing.minifix_placement_report as module

    source = inspect.getsource(module)

    assert "CNC" not in source
    assert "compiler" not in source.lower()
    assert "runtime" not in source.lower()


def test_minifix_placement_report_does_not_change_runtime_behavior():
    from domain.back_panel_engine import BackPanelEngine, BackPanelRule

    rule = BackPanelRule()

    assert BackPanelEngine.groove_width(rule) == rule.thickness + rule.groove_clearance
    assert BackPanelEngine.insertion_depth(rule) == rule.groove_depth
    assert BackPanelEngine.offset(rule) == rule.groove_offset
