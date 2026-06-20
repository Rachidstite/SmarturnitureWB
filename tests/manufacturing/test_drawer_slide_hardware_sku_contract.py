import inspect

from dataclasses import fields, is_dataclass


def test_drawer_slide_hardware_sku_contract_exists():
    from manufacturing.drawer_slide_hardware_sku import DrawerSlideHardwareSku

    assert is_dataclass(DrawerSlideHardwareSku)


def test_drawer_slide_hardware_sku_field_inventory_is_stable():
    from manufacturing.drawer_slide_hardware_sku import DrawerSlideHardwareSku

    assert [field.name for field in fields(DrawerSlideHardwareSku)] == [
        "sku",
        "manufacturer",
        "model",
        "revision",
        "category",
        "price",
    ]


def test_drawer_slide_hardware_sku_safe_defaults():
    from manufacturing.drawer_slide_hardware_sku import DrawerSlideHardwareSku

    sku = DrawerSlideHardwareSku()

    assert sku.sku == ""
    assert sku.manufacturer == ""
    assert sku.model == ""
    assert sku.revision == ""
    assert sku.category == ""
    assert sku.price == 0.0


def test_drawer_slide_hardware_sku_has_no_placement_or_generation_logic():
    import manufacturing.drawer_slide_hardware_sku as module

    source = inspect.getsource(module)

    assert "for " not in source
    assert "while " not in source
    assert "append(" not in source
    assert "hole" not in source.lower()
    assert "placement" not in source.lower()
    assert "geometry" not in source.lower()
    assert "generate" not in source.lower()
    assert "ManufacturingCompiler" not in source
    assert "FactoryDecisionBuilder" not in source
    assert "ProductionReadinessBuilder" not in source


def test_drawer_slide_hardware_sku_has_no_cnc_runtime_or_compiler_imports():
    import manufacturing.drawer_slide_hardware_sku as module

    source = inspect.getsource(module)

    assert "CNC" not in source
    assert "runtime" not in source.lower()
    assert "compiler" not in source.lower()


def test_drawer_slide_hardware_sku_does_not_change_runtime_behavior():
    from domain.back_panel_engine import BackPanelEngine, BackPanelRule

    rule = BackPanelRule()

    assert BackPanelEngine.groove_width(rule) == rule.thickness + rule.groove_clearance
    assert BackPanelEngine.insertion_depth(rule) == rule.groove_depth
    assert BackPanelEngine.offset(rule) == rule.groove_offset
