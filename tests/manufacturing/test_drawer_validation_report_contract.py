import inspect

from dataclasses import fields, is_dataclass


def test_drawer_validation_report_contract_exists():
    from manufacturing.drawer_validation_report import DrawerValidationReport

    assert is_dataclass(DrawerValidationReport)


def test_drawer_validation_report_field_inventory_is_stable():
    from manufacturing.drawer_validation_report import DrawerValidationReport

    assert [field.name for field in fields(DrawerValidationReport)] == [
        "is_valid",
        "manufacturing_ready",
        "slide_installation_valid",
        "clearance_valid",
        "hardware_complete",
        "blocking_issues",
        "warnings",
    ]


def test_drawer_validation_report_safe_defaults():
    from manufacturing.drawer_validation_report import DrawerValidationReport

    report = DrawerValidationReport()

    assert report.is_valid is False
    assert report.manufacturing_ready is False
    assert report.slide_installation_valid is False
    assert report.clearance_valid is False
    assert report.hardware_complete is False
    assert report.blocking_issues == []
    assert report.warnings == []


def test_drawer_validation_report_list_defaults_are_independent():
    from manufacturing.drawer_validation_report import DrawerValidationReport

    first = DrawerValidationReport()
    second = DrawerValidationReport()

    first.blocking_issues.append("issue")
    first.warnings.append("warning")

    assert second.blocking_issues == []
    assert second.warnings == []
    assert first.blocking_issues is not second.blocking_issues
    assert first.warnings is not second.warnings


def test_drawer_validation_report_has_no_runtime_or_geometry_logic():
    import manufacturing.drawer_validation_report as module

    source = inspect.getsource(module)

    assert "for " not in source
    assert "while " not in source
    assert "append(" not in source
    assert "geometry" not in source.lower()
    assert "calculate" not in source.lower()
    assert "generate" not in source.lower()
    assert "compiler" not in source.lower()
    assert "runtime" not in source.lower()


