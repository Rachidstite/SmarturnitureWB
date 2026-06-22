import inspect
from dataclasses import fields, is_dataclass


def test_hardware_bom_line_item_contract_exists_and_is_dataclass():
    from cost_intelligence.hardware_bom_cost_report import HardwareBomCostLineItem

    assert is_dataclass(HardwareBomCostLineItem)


def test_hardware_bom_line_item_field_inventory_is_stable():
    from cost_intelligence.hardware_bom_cost_report import HardwareBomCostLineItem

    assert [field.name for field in fields(HardwareBomCostLineItem)] == [
        "hardware_sku",
        "quantity",
        "unit_cost",
        "total_cost",
    ]


def test_hardware_bom_line_item_safe_defaults():
    from cost_intelligence.hardware_bom_cost_report import HardwareBomCostLineItem

    line_item = HardwareBomCostLineItem()

    assert line_item.hardware_sku == ""
    assert line_item.quantity == 0
    assert line_item.unit_cost == 0.0
    assert line_item.total_cost == 0.0


def test_hardware_bom_cost_report_contract_exists_and_is_dataclass():
    from cost_intelligence.hardware_bom_cost_report import HardwareBomCostReport

    assert is_dataclass(HardwareBomCostReport)


def test_hardware_bom_cost_report_field_inventory_is_stable():
    from cost_intelligence.hardware_bom_cost_report import HardwareBomCostReport

    assert [field.name for field in fields(HardwareBomCostReport)] == [
        "line_items",
        "total_hardware_cost",
        "warnings",
    ]


def test_hardware_bom_cost_report_safe_defaults():
    from cost_intelligence.hardware_bom_cost_report import HardwareBomCostReport

    report = HardwareBomCostReport()

    assert report.line_items == []
    assert report.total_hardware_cost == 0.0
    assert report.warnings == []


def test_hardware_bom_cost_builder_contract_exists():
    from cost_intelligence.hardware_bom_cost_builder import HardwareCostBuilder

    assert callable(HardwareCostBuilder().build)


def test_hardware_bom_cost_builder_build_signature_is_stable():
    from cost_intelligence.hardware_bom_cost_builder import HardwareCostBuilder

    build_signature = inspect.signature(HardwareCostBuilder.build)

    assert list(build_signature.parameters) == [
        "self",
        "hardware_bom_report",
        "pricing_catalog",
    ]


def test_hardware_bom_cost_builder_uses_bom_rows_as_source_of_truth():
    usage_report = _hardware_usage_report()
    bom_report = _hardware_bom_report(usage_report)

    cost_report = _build_cost_report(bom_report)

    assert _line_items_as_tuples(cost_report) == [
        ("MINIFIX_15_V1", 48, 1.5, 72.0),
        ("CONFIRMAT_50_V1", 16, 2.0, 32.0),
        ("SHELF_PIN_5MM", 24, 0.5, 12.0),
        ("DRAWER_SLIDE_STANDARD_450", 4, 20.0, 80.0),
    ]
    assert cost_report.total_hardware_cost == 196.0
    assert cost_report.warnings == []


def test_hardware_bom_cost_builder_missing_price_generates_warning_not_crash():
    usage_report = _hardware_usage_report()
    bom_report = _hardware_bom_report(usage_report)
    pricing_catalog = {
        "MINIFIX_15_V1": {"unit_price": 1.5},
        "SHELF_PIN_5MM": {"unit_price": 0.5},
    }

    cost_report = _build_cost_report(bom_report, pricing_catalog=pricing_catalog)

    assert _line_items_as_tuples(cost_report) == [
        ("MINIFIX_15_V1", 48, 1.5, 72.0),
        ("CONFIRMAT_50_V1", 16, 0.0, 0.0),
        ("SHELF_PIN_5MM", 24, 0.5, 12.0),
        ("DRAWER_SLIDE_STANDARD_450", 4, 0.0, 0.0),
    ]
    assert cost_report.total_hardware_cost == 84.0
    assert cost_report.warnings == [
        "Missing hardware price for CONFIRMAT_50_V1",
        "Missing hardware price for DRAWER_SLIDE_STANDARD_450",
    ]


def test_hardware_bom_cost_builder_may_use_registry_but_not_geometry_or_intent():
    import cost_intelligence.hardware_bom_cost_builder as module

    source = inspect.getsource(module)

    assert "hardware_sku" in source
    assert "hardware_intent" not in source
    assert "geometry" not in source.lower()
    assert "rule" not in source.lower()


def test_hardware_bom_cost_builder_does_not_mutate_bom_report():
    bom_report = _hardware_bom_report(_hardware_usage_report())
    original_rows = [
        (row.hardware_sku, row.quantity)
        for row in bom_report.bom_rows
    ]

    try:
        _build_cost_report(bom_report)
    except Exception:
        pass

    assert [
        (row.hardware_sku, row.quantity)
        for row in bom_report.bom_rows
    ] == original_rows


def test_manufacturing_package_remains_unchanged_for_cost_contract():
    from manufacturing.manufacturing_package import ManufacturingPackage

    assert [field.name for field in fields(ManufacturingPackage)] == [
        "panels",
        "materials",
        "machining_operations",
        "edge_operations",
        "warnings",
    ]
    assert not hasattr(ManufacturingPackage, "hardware_bom_cost_report")
    assert not hasattr(ManufacturingPackage, "build_hardware_bom_cost_report")


def _build_cost_report(hardware_bom_report, pricing_catalog=None):
    from cost_intelligence.hardware_bom_cost_builder import HardwareCostBuilder

    return HardwareCostBuilder().build(
        hardware_bom_report,
        pricing_catalog=pricing_catalog,
    )


def _hardware_usage_report():
    from manufacturing.hardware_usage_report import HardwareUsageReport

    return HardwareUsageReport(
        hardware_sku_counts={
            "MINIFIX_15_V1": 48,
            "CONFIRMAT_50_V1": 16,
            "SHELF_PIN_5MM": 24,
            "DRAWER_SLIDE_STANDARD_450": 4,
        },
        hardware_family_counts={
            "MINIFIX": {"MINIFIX_15_V1": 48},
            "CONFIRMAT": {"CONFIRMAT_50_V1": 16},
        },
        hardware_intent_counts={
            "INTENT_MINIFIX_15": {"MINIFIX_15_V1": 48},
            "INTENT_CONFIRMAT_50": {"CONFIRMAT_50_V1": 16},
        },
    )


def _hardware_bom_report(usage_report):
    from manufacturing.hardware_bom_builder import HardwareBomBuilder

    return HardwareBomBuilder().build(usage_report)


def _line_items_as_tuples(report):
    return [
        (
            item.hardware_sku,
            item.quantity,
            item.unit_cost,
            item.total_cost,
        )
        for item in getattr(report, "line_items", []) or []
    ]
