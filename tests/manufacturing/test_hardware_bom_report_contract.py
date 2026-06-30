import inspect
from dataclasses import fields, is_dataclass


def test_hardware_bom_row_contract_exists_and_is_dataclass():
    from manufacturing.hardware_bom_report import HardwareBomRow

    assert is_dataclass(HardwareBomRow)


def test_hardware_bom_row_field_inventory_is_stable():
    from manufacturing.hardware_bom_report import HardwareBomRow

    assert [field.name for field in fields(HardwareBomRow)] == [
        "bom_category",
        "sku",
        "description",
        "quantity",
        "unit",
        "component_reference",
        "cabinet_reference",
        "hardware_category",
        "source_operation_references",
    ]


def test_hardware_bom_row_safe_defaults():
    from manufacturing.hardware_bom_report import HardwareBomRow

    row = HardwareBomRow()

    assert row.bom_category == "HARDWARE"
    assert row.sku == ""
    assert row.hardware_sku == ""
    assert row.description == ""
    assert row.quantity == 0
    assert row.unit == "pcs"
    assert row.component_reference == ()
    assert row.cabinet_reference == ()
    assert row.hardware_category == ""
    assert row.source_operation_references == ()


def test_hardware_bom_report_contract_exists_and_is_dataclass():
    from manufacturing.hardware_bom_report import HardwareBomReport

    assert is_dataclass(HardwareBomReport)


def test_hardware_bom_report_field_inventory_is_stable():
    from manufacturing.hardware_bom_report import HardwareBomReport

    assert [field.name for field in fields(HardwareBomReport)] == [
        "bom_rows",
        "warnings",
    ]


def test_hardware_bom_report_safe_defaults():
    from manufacturing.hardware_bom_report import HardwareBomReport

    report = HardwareBomReport()

    assert report.bom_rows == []
    assert report.warnings == []


def test_hardware_bom_builder_contract_exists():
    from manufacturing.hardware_bom_builder import HardwareBomBuilder

    assert callable(HardwareBomBuilder().build)


def test_hardware_bom_builder_build_signature_is_stable():
    from manufacturing.hardware_bom_builder import HardwareBomBuilder

    build_signature = inspect.signature(HardwareBomBuilder.build)

    assert list(build_signature.parameters) == [
        "self",
        "hardware_usage_report",
    ]


def test_hardware_bom_builder_uses_hardware_sku_counts_as_source_of_truth():
    usage_report = _hardware_usage_report_with_mixed_identity_data()

    report = _build_hardware_bom_report(usage_report)

    assert _bom_rows_as_tuples(report) == [
        ("MINIFIX_15_V1", 48),
        ("CONFIRMAT_50_V1", 16),
        ("SHELF_PIN_5MM", 24),
        ("DRAWER_SLIDE_STANDARD_450", 4),
    ]


def test_hardware_bom_builder_ignores_hardware_intent_and_family_counts():
    usage_report = _hardware_usage_report_with_mixed_identity_data()

    report = _build_hardware_bom_report(usage_report)

    assert _bom_rows_as_tuples(report) == [
        ("MINIFIX_15_V1", 48),
        ("CONFIRMAT_50_V1", 16),
        ("SHELF_PIN_5MM", 24),
        ("DRAWER_SLIDE_STANDARD_450", 4),
    ]


def test_hardware_bom_builder_does_not_require_geometry_rule_or_registry_logic():
    import manufacturing.hardware_bom_builder as module

    source = inspect.getsource(module)

    assert "geometry" not in source.lower()
    assert "hardwareintent" not in source.lower()
    assert "hardware_intent" not in source
    assert "HardwareRegistry" not in source
    assert "hardware_library" not in source
    assert "rule" not in source.lower()


def test_hardware_bom_report_supports_future_cost_integration_without_touching_usage():
    usage_report = _hardware_usage_report_with_mixed_identity_data()
    original_counts = dict(usage_report.hardware_sku_counts)

    report = _build_hardware_bom_report(usage_report)

    assert hasattr(report, "bom_rows")
    assert hasattr(report, "warnings")
    assert dict(usage_report.hardware_sku_counts) == original_counts


def test_manufacturing_package_remains_unchanged_for_bom_contract():
    from manufacturing.manufacturing_package import ManufacturingPackage

    assert [field.name for field in fields(ManufacturingPackage)] == [
        "panels",
        "materials",
        "machining_operations",
        "edge_operations",
        "warnings",
    ]
    assert not hasattr(ManufacturingPackage, "hardware_bom_report")
    assert not hasattr(ManufacturingPackage, "build_hardware_bom_report")
    assert not hasattr(ManufacturingPackage, "generate_hardware_bom_report")


def test_manufacturing_package_source_contains_no_bom_entrypoint():
    import manufacturing.manufacturing_package as module

    source = inspect.getsource(module)

    assert "hardware_bom_report" not in source
    assert "build_hardware_bom_report" not in source
    assert "generate_hardware_bom_report" not in source


def _build_hardware_bom_report(hardware_usage_report):
    from manufacturing.hardware_bom_builder import HardwareBomBuilder

    return HardwareBomBuilder().build(hardware_usage_report)


def _bom_rows_as_tuples(report):
    return [
        (row.hardware_sku, row.quantity)
        for row in getattr(report, "bom_rows", []) or []
    ]


def _hardware_usage_report_with_mixed_identity_data():
    from manufacturing.hardware_usage_report import HardwareUsageReport

    return HardwareUsageReport(
        hardware_sku_counts={
            "MINIFIX_15_V1": 48,
            "CONFIRMAT_50_V1": 16,
            "SHELF_PIN_5MM": 24,
            "DRAWER_SLIDE_STANDARD_450": 4,
        },
        hardware_family_counts={
            "MINIFIX": {"MINIFIX_15_V1": 999},
            "CONFIRMAT": {"CONFIRMAT_50_V1": 999},
        },
        hardware_intent_counts={
            "INTENT_MINIFIX_15": {"MINIFIX_15_V1": 999},
            "INTENT_CONFIRMAT_50": {"CONFIRMAT_50_V1": 999},
        },
    )
