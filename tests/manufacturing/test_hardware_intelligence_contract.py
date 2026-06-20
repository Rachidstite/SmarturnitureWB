import inspect

from dataclasses import fields, is_dataclass


def test_hardware_intelligence_report_contract_exists():
    from manufacturing.hardware_intelligence_report import HardwareIntelligenceReport

    assert is_dataclass(HardwareIntelligenceReport)


def test_hardware_intelligence_report_field_inventory_is_stable():
    from manufacturing.hardware_intelligence_report import HardwareIntelligenceReport

    assert [field.name for field in fields(HardwareIntelligenceReport)] == [
        "hardware_family",
        "total_hardware_items",
        "total_host_holes",
        "total_target_holes",
        "total_face_holes",
        "total_edge_holes",
        "requires_review",
        "manufacturing_warning",
        "recommended_action",
    ]


def test_hardware_intelligence_report_safe_defaults():
    from manufacturing.hardware_intelligence_report import HardwareIntelligenceReport

    report = HardwareIntelligenceReport()

    assert report.hardware_family == ""
    assert report.total_hardware_items == 0
    assert report.total_host_holes == 0
    assert report.total_target_holes == 0
    assert report.total_face_holes == 0
    assert report.total_edge_holes == 0
    assert report.requires_review is False
    assert report.manufacturing_warning == ""
    assert report.recommended_action == ""


def test_hardware_intelligence_report_has_no_placement_or_hole_generation_logic():
    import manufacturing.hardware_intelligence_report as module

    source = inspect.getsource(module)

    assert "for " not in source
    assert "while " not in source
    assert "append(" not in source
    assert "placement" not in source.lower()
    assert "generate" not in source.lower()
    assert "geometry" not in source.lower()
    assert "calculate" not in source.lower()
    assert "ManufacturingCompiler" not in source
    assert "HardwarePlacement" not in source


def test_hardware_intelligence_report_has_no_compiler_runtime_cnc_cost_or_quotation_imports():
    import manufacturing.hardware_intelligence_report as module

    source = inspect.getsource(module)

    assert "compiler" not in source.lower()
    assert "runtime" not in source.lower()
    assert "CNC" not in source
    assert "cost_intelligence" not in source
    assert "quotation" not in source.lower()
    assert "HardwareRegistry" not in source
    assert "HardwareSpec" not in source
    assert "HoleSpec" not in source


def test_hardware_intelligence_report_does_not_change_runtime_behavior():
    from domain.back_panel_engine import BackPanelEngine, BackPanelRule

    rule = BackPanelRule()

    assert BackPanelEngine.groove_width(rule) == rule.thickness + rule.groove_clearance
    assert BackPanelEngine.insertion_depth(rule) == rule.groove_depth
    assert BackPanelEngine.offset(rule) == rule.groove_offset
