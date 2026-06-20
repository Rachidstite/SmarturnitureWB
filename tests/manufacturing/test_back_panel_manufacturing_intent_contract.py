import inspect

from dataclasses import fields, is_dataclass


def test_back_panel_manufacturing_intent_report_exists():
    from manufacturing.back_panel_manufacturing_intent_report import (
        BackPanelManufacturingIntentReport,
    )

    assert is_dataclass(BackPanelManufacturingIntentReport)


def test_back_panel_manufacturing_intent_report_field_inventory_is_stable():
    from manufacturing.back_panel_manufacturing_intent_report import (
        BackPanelManufacturingIntentReport,
    )

    assert [field.name for field in fields(BackPanelManufacturingIntentReport)] == [
        "fixing_intent",
        "assembly_intent",
        "manufacturing_intent",
        "requires_groove",
        "requires_fasteners",
        "requires_center_support",
        "fastener_type",
        "back_panel_method",
        "cnc_preparation_required",
        "visual_manufacturing_intent_required",
    ]


def test_back_panel_manufacturing_intent_report_safe_defaults():
    from manufacturing.back_panel_manufacturing_intent_report import (
        BackPanelManufacturingIntentReport,
    )

    report = BackPanelManufacturingIntentReport()

    assert report.fixing_intent == ""
    assert report.assembly_intent == ""
    assert report.manufacturing_intent == ""
    assert report.requires_groove is False
    assert report.requires_fasteners is False
    assert report.requires_center_support is False
    assert report.fastener_type == ""
    assert report.back_panel_method == ""
    assert report.cnc_preparation_required is False
    assert report.visual_manufacturing_intent_required is False


def test_back_panel_manufacturing_intent_report_has_no_generation_logic():
    import manufacturing.back_panel_manufacturing_intent_report as module

    source = inspect.getsource(module)

    assert "for " not in source
    assert "while " not in source
    assert "append(" not in source
    assert "ManufacturingCompiler" not in source
    assert "FactoryDecisionBuilder" not in source
    assert "ProductionReadinessBuilder" not in source


def test_back_panel_manufacturing_intent_report_has_no_cnc_or_runtime_imports():
    import manufacturing.back_panel_manufacturing_intent_report as module

    source = inspect.getsource(module)

    assert "CNC" not in source
    assert "compiler" not in source.lower()
    assert "runtime" not in source.lower()


def test_back_panel_manufacturing_intent_report_does_not_change_runtime_behavior():
    from domain.back_panel_engine import BackPanelEngine, BackPanelRule

    rule = BackPanelRule()

    assert BackPanelEngine.groove_width(rule) == rule.thickness + rule.groove_clearance
    assert BackPanelEngine.insertion_depth(rule) == rule.groove_depth
    assert BackPanelEngine.offset(rule) == rule.groove_offset
