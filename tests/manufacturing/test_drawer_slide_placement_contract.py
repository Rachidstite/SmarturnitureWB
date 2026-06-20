import inspect

from dataclasses import fields, is_dataclass


def test_drawer_slide_placement_report_contract_exists():
    from manufacturing.drawer_slide_placement_report import DrawerSlidePlacementReport

    assert is_dataclass(DrawerSlidePlacementReport)


def test_drawer_slide_placement_report_field_inventory_is_stable():
    from manufacturing.drawer_slide_placement_report import DrawerSlidePlacementReport

    assert [field.name for field in fields(DrawerSlidePlacementReport)] == [
        "drawer_id",
        "slide_side",
        "cabinet_panel_id",
        "drawer_panel_id",
        "x_position",
        "y_position",
        "z_position",
        "mounting_face",
        "placement_type",
    ]


def test_drawer_slide_placement_report_safe_defaults():
    from manufacturing.drawer_slide_placement_report import DrawerSlidePlacementReport

    report = DrawerSlidePlacementReport()

    assert report.drawer_id == ""
    assert report.slide_side == ""
    assert report.cabinet_panel_id == ""
    assert report.drawer_panel_id == ""
    assert report.x_position == 0.0
    assert report.y_position == 0.0
    assert report.z_position == 0.0
    assert report.mounting_face == ""
    assert report.placement_type == ""


def test_drawer_slide_placement_report_has_no_placement_or_geometry_logic():
    import manufacturing.drawer_slide_placement_report as module

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


def test_drawer_slide_placement_report_has_no_cnc_runtime_or_compiler_imports():
    import manufacturing.drawer_slide_placement_report as module

    source = inspect.getsource(module)

    assert "CNC" not in source
    assert "runtime" not in source.lower()
    assert "compiler" not in source.lower()


def test_drawer_slide_placement_report_does_not_change_runtime_behavior():
    from domain.back_panel_engine import BackPanelEngine, BackPanelRule

    rule = BackPanelRule()

    assert BackPanelEngine.groove_width(rule) == rule.thickness + rule.groove_clearance
    assert BackPanelEngine.insertion_depth(rule) == rule.groove_depth
    assert BackPanelEngine.offset(rule) == rule.groove_offset
