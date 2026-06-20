import inspect

from dataclasses import fields, is_dataclass


def test_minifix_hardware_sku_contract_exists():
    from manufacturing.minifix_hardware_sku import MinifixHardwareSku

    assert is_dataclass(MinifixHardwareSku)


def test_minifix_hardware_sku_field_inventory_is_stable():
    from manufacturing.minifix_hardware_sku import MinifixHardwareSku

    assert [field.name for field in fields(MinifixHardwareSku)] == [
        "sku",
        "manufacturer",
        "description",
        "diameter",
        "depth",
        "cam_diameter",
        "cam_depth",
        "compatible_panel_thickness",
    ]


def test_minifix_hardware_sku_safe_defaults():
    from manufacturing.minifix_hardware_sku import MinifixHardwareSku

    sku = MinifixHardwareSku()

    assert sku.sku == ""
    assert sku.manufacturer == ""
    assert sku.description == ""
    assert sku.diameter == 0.0
    assert sku.depth == 0.0
    assert sku.cam_diameter == 0.0
    assert sku.cam_depth == 0.0
    assert sku.compatible_panel_thickness == 0.0


def test_minifix_hardware_sku_has_no_hole_generation_or_placement_logic():
    import manufacturing.minifix_hardware_sku as module

    source = inspect.getsource(module)

    assert "for " not in source
    assert "while " not in source
    assert "append(" not in source
    assert "placement" not in source.lower()
    assert "hole" not in source.lower()
    assert "ManufacturingCompiler" not in source
    assert "FactoryDecisionBuilder" not in source
    assert "ProductionReadinessBuilder" not in source


def test_minifix_hardware_sku_has_no_cnc_or_runtime_imports():
    import manufacturing.minifix_hardware_sku as module

    source = inspect.getsource(module)

    assert "CNC" not in source
    assert "compiler" not in source.lower()
    assert "runtime" not in source.lower()


def test_minifix_hardware_sku_does_not_change_runtime_behavior():
    from domain.back_panel_engine import BackPanelEngine, BackPanelRule

    rule = BackPanelRule()

    assert BackPanelEngine.groove_width(rule) == rule.thickness + rule.groove_clearance
    assert BackPanelEngine.insertion_depth(rule) == rule.groove_depth
    assert BackPanelEngine.offset(rule) == rule.groove_offset
