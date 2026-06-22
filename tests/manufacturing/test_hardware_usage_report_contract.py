import inspect
from dataclasses import fields, is_dataclass


def test_hardware_usage_report_contract_exists_and_is_dataclass():
    from manufacturing.hardware_usage_report import HardwareUsageReport

    assert is_dataclass(HardwareUsageReport)


def test_hardware_usage_report_field_inventory_is_stable():
    from manufacturing.hardware_usage_report import HardwareUsageReport

    assert [field.name for field in fields(HardwareUsageReport)] == [
        "hardware_sku_counts",
        "hardware_family_counts",
        "hardware_intent_counts",
    ]


def test_hardware_usage_report_safe_defaults():
    from manufacturing.hardware_usage_report import HardwareUsageReport

    report = HardwareUsageReport()

    assert report.hardware_sku_counts == {}
    assert report.hardware_family_counts == {}
    assert report.hardware_intent_counts == {}


def test_hardware_usage_builder_contract_exists():
    from manufacturing.hardware_usage_builder import HardwareUsageBuilder

    assert callable(HardwareUsageBuilder().build)


def test_hardware_usage_builder_build_signature_is_stable():
    from manufacturing.hardware_usage_builder import HardwareUsageBuilder

    build_signature = inspect.signature(HardwareUsageBuilder.build)

    assert list(build_signature.parameters) == [
        "self",
        "manufacturing_package",
    ]


def test_hardware_usage_builder_counts_runtime_metadata_by_sku_family_and_intent():
    package = _package_with_runtime_identity_metadata()

    report = _build_hardware_usage_report(package)

    assert report.hardware_sku_counts == {
        "MINIFIX_15_V1": 48,
        "CONFIRMAT_50_V1": 16,
        "SHELF_PIN_5MM": 24,
        "DRAWER_SLIDE_STANDARD_450": 4,
    }
    assert report.hardware_family_counts == {
        "MINIFIX": {"MINIFIX_15_V1": 48},
        "CONFIRMAT": {"CONFIRMAT_50_V1": 16},
        "SHELF_PIN": {"SHELF_PIN_5MM": 24},
        "DRAWER_SLIDE": {"DRAWER_SLIDE_STANDARD_450": 4},
    }
    assert report.hardware_intent_counts == {
        "INTENT_MINIFIX_15": {"MINIFIX_15_V1": 48},
        "INTENT_CONFIRMAT_50": {"CONFIRMAT_50_V1": 16},
        "INTENT_SHELF_PIN": {"SHELF_PIN_5MM": 24},
        "INTENT_DRAWER_SLIDE": {"DRAWER_SLIDE_STANDARD_450": 4},
    }


def test_hardware_usage_builder_ignores_operations_without_complete_identity():
    package = _package_with_incomplete_identity_metadata()

    report = _build_hardware_usage_report(package)

    assert report.hardware_sku_counts == {
        "MINIFIX_15_V1": 2,
    }
    assert report.hardware_family_counts == {
        "MINIFIX": {"MINIFIX_15_V1": 2},
    }
    assert report.hardware_intent_counts == {
        "INTENT_MINIFIX_15": {"MINIFIX_15_V1": 2},
    }


def test_hardware_usage_builder_uses_runtime_metadata_not_geometry():
    package = _package_with_runtime_identity_metadata()

    report = _build_hardware_usage_report(package)

    assert report.hardware_sku_counts["DRAWER_SLIDE_STANDARD_450"] == 4
    assert report.hardware_intent_counts["INTENT_DRAWER_SLIDE"] == {
        "DRAWER_SLIDE_STANDARD_450": 4,
    }


def test_hardware_usage_builder_does_not_require_registry_lookups_or_geometry_inference():
    import manufacturing.hardware_usage_builder as module

    source = inspect.getsource(module)

    assert "HardwareRegistry" not in source
    assert "hardware_library" not in source
    assert "geometry" not in source.lower()
    assert "diameter" not in source.lower()
    assert "depth" not in source.lower()
    assert "face" not in source.lower()
    assert "axis" not in source.lower()


def test_manufacturing_package_remains_a_pure_data_container():
    from manufacturing.manufacturing_package import ManufacturingPackage

    assert [field.name for field in fields(ManufacturingPackage)] == [
        "panels",
        "materials",
        "machining_operations",
        "edge_operations",
        "warnings",
    ]
    assert not hasattr(ManufacturingPackage, "hardware_usage_report")
    assert not hasattr(ManufacturingPackage, "build_hardware_usage_report")
    assert not hasattr(ManufacturingPackage, "generate_hardware_usage_report")


def test_manufacturing_package_source_contains_no_hardware_usage_entrypoint():
    import manufacturing.manufacturing_package as module

    source = inspect.getsource(module)

    assert "hardware_usage_report" not in source
    assert "build_hardware_usage_report" not in source
    assert "generate_hardware_usage_report" not in source


def test_hardware_usage_builder_does_not_mutate_runtime_operations():
    package = _package_with_runtime_identity_metadata()
    original_metadata = [
        dict(operation.metadata)
        for operation in package.machining_operations
    ]

    try:
        _build_hardware_usage_report(package)
    except Exception:
        pass

    assert [dict(operation.metadata) for operation in package.machining_operations] == original_metadata


def _build_hardware_usage_report(package):
    from manufacturing.hardware_usage_builder import HardwareUsageBuilder

    return HardwareUsageBuilder().build(package)


def _package_with_runtime_identity_metadata():
    from manufacturing.manufacturing_package import ManufacturingPackage
    from manufacturing.unified_manufacturing_operation import (
        UnifiedManufacturingOperation,
    )

    def operation(sku, family, intent, count, diameter, depth):
        return [
            UnifiedManufacturingOperation(
                operation_type="DRILL",
                diameter=diameter,
                depth=depth,
                face="LEFT",
                metadata={
                    "hardware_family": family,
                    "hardware_sku": sku,
                    "hardware_intent": intent,
                },
            )
            for _ in range(count)
        ]

    machining_operations = []
    machining_operations.extend(
        operation("MINIFIX_15_V1", "MINIFIX", "INTENT_MINIFIX_15", 48, 15.0, 14.0)
    )
    machining_operations.extend(
        operation("CONFIRMAT_50_V1", "CONFIRMAT", "INTENT_CONFIRMAT_50", 16, 7.0, 18.0)
    )
    machining_operations.extend(
        operation("SHELF_PIN_5MM", "SHELF_PIN", "INTENT_SHELF_PIN", 24, 5.0, 12.0)
    )
    machining_operations.extend(
        operation(
            "DRAWER_SLIDE_STANDARD_450",
            "DRAWER_SLIDE",
            "INTENT_DRAWER_SLIDE",
            4,
            3.0,
            12.0,
        )
    )

    machining_operations.append(
        UnifiedManufacturingOperation(
            operation_type="DRILL",
            diameter=999.0,
            depth=999.0,
            face="LEFT",
            metadata={},
        )
    )

    return ManufacturingPackage(
        machining_operations=machining_operations,
    )


def _package_with_incomplete_identity_metadata():
    from manufacturing.manufacturing_package import ManufacturingPackage
    from manufacturing.unified_manufacturing_operation import (
        UnifiedManufacturingOperation,
    )

    return ManufacturingPackage(
        machining_operations=[
            UnifiedManufacturingOperation(
                operation_type="DRILL",
                diameter=15.0,
                depth=14.0,
                metadata={
                    "hardware_family": "MINIFIX",
                    "hardware_sku": "MINIFIX_15_V1",
                },
            ),
            UnifiedManufacturingOperation(
                operation_type="DRILL",
                diameter=15.0,
                depth=14.0,
                metadata={
                    "hardware_family": "MINIFIX",
                    "hardware_intent": "INTENT_MINIFIX_15",
                },
            ),
            UnifiedManufacturingOperation(
                operation_type="DRILL",
                diameter=15.0,
                depth=14.0,
                metadata={
                    "hardware_sku": "MINIFIX_15_V1",
                    "hardware_intent": "INTENT_MINIFIX_15",
                },
            ),
            UnifiedManufacturingOperation(
                operation_type="DRILL",
                diameter=12.0,
                depth=99.0,
                metadata={},
            ),
            UnifiedManufacturingOperation(
                operation_type="DRILL",
                diameter=15.0,
                depth=14.0,
                metadata={
                    "hardware_family": "MINIFIX",
                    "hardware_sku": "MINIFIX_15_V1",
                    "hardware_intent": "INTENT_MINIFIX_15",
                },
            ),
            UnifiedManufacturingOperation(
                operation_type="DRILL",
                diameter=18.0,
                depth=3.0,
                metadata={
                    "hardware_family": "MINIFIX",
                    "hardware_sku": "MINIFIX_15_V1",
                    "hardware_intent": "INTENT_MINIFIX_15",
                },
            ),
        ]
    )
