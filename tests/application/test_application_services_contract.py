"""Contract tests for the Application Layer.

Validates:
  - Application services call real existing components (no mock fallback).
  - Returned result format is stable (ApplicationServiceResult).
  - No mock values, no REAL_ENGINE_AVAILABLE guards in code logic.
"""

import inspect
import unittest
from typing import Any
from unittest.mock import patch

# --- Module-level imports ---

import application.project_application_service as project_svc_module
import application.engineering_application_service as eng_svc_module
import application.manufacturing_application_service as mfg_svc_module

from application.application_service_result import ApplicationServiceResult
from application.base_application_service import BaseApplicationService
from application.project_application_service import ProjectApplicationService
from application.engineering_application_service import EngineeringApplicationService
from application.manufacturing_application_service import (
    ManufacturingApplicationService,
)
from domain.base_cabinet_specification import BaseCabinetSpecification
from engine.cabinet import Cabinet
from domain.base_cabinet_manufacturing_outputs_entry import (
    BaseCabinetManufacturingOutputsEntryResult,
)
from domain.base_cabinet_product_result import BaseCabinetProductResult
from manufacturing.edge_spec import EdgeSpec
from manufacturing.manufacturing_package import ManufacturingPackage
from manufacturing.panel_spec import PanelSpec
from manufacturing.unified_manufacturing_operation import (
    UnifiedManufacturingOperation,
)
from shared.roles import NodeRole

# ---- helpers ----

# Reused from existing domain/engineering contract tests.
class FakeCabinetBuilder:
    """Minimal stand-in for engine.cabinet_builder.CabinetBuilder.

    Sets a scene_graph on the cabinet, mirroring the real builder's
    post-build contract (``cabinet.graph = builder.scene_graph``).
    """
    instances_created = 0
    build_calls = 0
    last_cabinet = None

    def __init__(self):
        type(self).instances_created += 1
        self.scene_graph = object()

    def build(self, cabinet: Any) -> None:
        type(self).build_calls += 1
        type(self).last_cabinet = cabinet
        # The real CabinetBuilder attaches scene_graph after build;
        # this fake mirrors that contract so downstream consumers
        # (manufacturing outputs entry, product workflow) can proceed.
        cabinet.graph = self.scene_graph
        cabinet.scene_graph = self.scene_graph


def _reset_fake_cabinet_builder() -> None:
    FakeCabinetBuilder.instances_created = 0
    FakeCabinetBuilder.build_calls = 0
    FakeCabinetBuilder.last_cabinet = None


# ---- Fake results for entry-point patching ----

_FAKE_MANUFACTURING_RESULT = BaseCabinetManufacturingOutputsEntryResult(
    cut_list=object(),
    manufacturing_package=ManufacturingPackage(
        panels=[
            PanelSpec(
                identity="shelf-01",
                role=NodeRole.SHELF,
                width=600.0,
                height=500.0,
                thickness=18.0,
                material="MDF_18MM",
                edge_spec=EdgeSpec(top="ABS_1MM"),
            )
        ],
        machining_operations=[
            UnifiedManufacturingOperation(operation_type="DRILL")
        ],
        edge_operations=[
            UnifiedManufacturingOperation(operation_type="EDGE_BANDING")
        ],
    ),
    metadata={"door_count": 2},
)

_FAKE_PROJECT_RESULT = BaseCabinetProductResult(
    specification=BaseCabinetSpecification(),
    scenario=object(),
    engineering=object(),
    validation=object(),
    manufacturing_outputs=object(),
    cost=object(),
    commercial=object(),
    diagnostics=("pattern-warning",),
)


# The domain module where CabinetBuilder lives (patched by existing tests too).
import domain.base_cabinet_engineering_entry as _eng_entry_module


def _source_lines_without_comments(mod: object) -> str:
    """Return source stripped of comment-only lines and docstrings.

    This lets us check for forbidden patterns (mock values, fake fallback)
    in actual code logic rather than in comments or docstrings.
    """
    raw = inspect.getsource(mod)
    lines = raw.splitlines(keepends=True)
    filtered: list[str] = []
    in_docstring: str | None = None
    for line in lines:
        stripped = line.strip()
        # Strip comment-only lines
        if stripped.startswith("#"):
            continue
        # Track multi-line docstrings
        if in_docstring:
            if in_docstring in stripped:
                in_docstring = None
            continue
        for delim in ('"""', "'''"):
            if stripped.startswith(delim) or stripped == delim:
                remainder = stripped[len(delim):]
                if delim in remainder:
                    # Single-line docstring — skip the whole line
                    in_docstring = None
                else:
                    in_docstring = delim
                break
        else:
            # Not a docstring line — keep
            filtered.append(line)
    return "".join(filtered)


# ---------------------------------------------------------------------------
# ApplicationServiceResult
# ---------------------------------------------------------------------------

class TestApplicationServiceResultContract(unittest.TestCase):
    """ApplicationServiceResult shape and behaviour."""

    def test_default_success_is_true(self):
        result = ApplicationServiceResult()
        self.assertTrue(result.success)
        self.assertTrue(bool(result))

    def test_stores_data(self):
        result = ApplicationServiceResult(data={"key": "value"})
        self.assertEqual(result.data, {"key": "value"})

    def test_stores_errors(self):
        result = ApplicationServiceResult(success=False, errors=("fail",))
        self.assertFalse(result)
        self.assertIn("fail", result.errors)

    def test_stores_diagnostics(self):
        diag = ("violation-1", "warning-2")
        result = ApplicationServiceResult(diagnostics=diag)
        self.assertEqual(result.diagnostics, diag)

    def test_immutable_via_frozen_dataclass(self):
        result = ApplicationServiceResult()
        with self.assertRaises(Exception):
            result.success = False  # type: ignore[misc]

    def test_no_mock_fields_in_code(self):
        """Verify ApplicationServiceResult has no mock/fake-related logic."""
        code = _source_lines_without_comments(ApplicationServiceResult)
        self.assertNotIn("mock", code.lower())
        self.assertNotIn("fake", code.lower())
        self.assertNotIn("REAL_ENGINE_AVAILABLE", code)


# ---------------------------------------------------------------------------
# BaseApplicationService
# ---------------------------------------------------------------------------

class TestBaseApplicationServiceContract(unittest.TestCase):
    """BaseApplicationService enforces the contract pattern."""

    def test_execute_catches_and_wraps_exceptions(self):
        class _RaisingService(BaseApplicationService):
            def _execute(self, **kwargs):  # type: ignore[override]
                raise RuntimeError("something went wrong")

        result = _RaisingService().execute()
        self.assertFalse(result.success)
        self.assertIsNone(result.data)
        self.assertTrue(any("RuntimeError" in e for e in result.errors))

    def test_abstract_class_cannot_be_instantiated(self):
        with self.assertRaises(TypeError):
            BaseApplicationService()  # type: ignore[abstract]


# ---------------------------------------------------------------------------
# EngineeringApplicationService
# ---------------------------------------------------------------------------

class TestEngineeringApplicationServiceContract(unittest.TestCase):
    """Must call the real engineering entry point with real params."""

    def setUp(self):
        _reset_fake_cabinet_builder()

    def test_calls_build_base_cabinet_engineering_cabinet(self):
        """Verify delegation to the real engineering entry point."""
        svc = EngineeringApplicationService()
        spec = BaseCabinetSpecification(width_mm=900.0)

        with patch.object(
            _eng_entry_module,
            "CabinetBuilder",
            new=FakeCabinetBuilder,
        ):
            with patch.object(
                eng_svc_module,
                "build_base_cabinet_engineering_cabinet",
                wraps=eng_svc_module.build_base_cabinet_engineering_cabinet,
            ) as spy:
                result = svc.execute(specification=spec)

        self.assertTrue(result.success)
        spy.assert_called_once()
        self.assertIsInstance(result.data["cabinet"], Cabinet)
        self.assertEqual(result.data["specification"], spec)

    def test_returns_application_service_result(self):
        svc = EngineeringApplicationService()

        with patch.object(
            _eng_entry_module, "CabinetBuilder", new=FakeCabinetBuilder,
        ):
            result = svc.execute(specification=BaseCabinetSpecification())

        self.assertIsInstance(result, ApplicationServiceResult)
        self.assertIn("cabinet", result.data)
        self.assertIn("specification", result.data)
        self.assertIn("metadata", result.data)

    def test_default_specification_creates_valid_cabinet(self):
        svc = EngineeringApplicationService()

        with patch.object(
            _eng_entry_module, "CabinetBuilder", new=FakeCabinetBuilder,
        ):
            result = svc.execute()

        self.assertTrue(result.success)
        self.assertIsInstance(result.data["cabinet"], Cabinet)

    def test_no_mock_fallback_in_code(self):
        """Only code lines are checked; comments and docstrings are ignored."""
        code = _source_lines_without_comments(eng_svc_module)
        self.assertNotIn("mock", code.lower())
        self.assertNotIn("REAL_ENGINE_AVAILABLE", code)
        self.assertNotIn("fake", code.lower())

    def test_no_new_engines_imported(self):
        """Verify only existing domain entry points are used."""
        source = inspect.getsource(eng_svc_module)
        self.assertIn("build_base_cabinet_engineering_cabinet", source)
        self.assertNotIn("ManufacturingRuntimePipelineBuilder", source)


# ---------------------------------------------------------------------------
# ManufacturingApplicationService
# ---------------------------------------------------------------------------

class TestManufacturingApplicationServiceContract(unittest.TestCase):
    """Must call the real manufacturing outputs entry point."""

    def test_calls_build_base_cabinet_manufacturing_outputs_entry(self):
        """Verify delegation: service calls the real entry point."""
        svc = ManufacturingApplicationService()
        spec = BaseCabinetSpecification()

        with patch.object(
            mfg_svc_module,
            "build_base_cabinet_manufacturing_outputs_entry",
            return_value=_FAKE_MANUFACTURING_RESULT,
        ) as spy:
            result = svc.execute(specification=spec)

        self.assertTrue(result.success)
        spy.assert_called_once_with(spec)
        self.assertIsInstance(
            result.data["manufacturing_outputs"],
            BaseCabinetManufacturingOutputsEntryResult,
        )
        self.assertIsNotNone(result.data["cut_list"])
        self.assertIsNotNone(result.data["manufacturing_package"])

    def test_returns_application_service_result(self):
        svc = ManufacturingApplicationService()
        with patch.object(
            mfg_svc_module,
            "build_base_cabinet_manufacturing_outputs_entry",
            return_value=_FAKE_MANUFACTURING_RESULT,
        ):
            result = svc.execute(specification=BaseCabinetSpecification())
        self.assertIsInstance(result, ApplicationServiceResult)
        self.assertIn("manufacturing_outputs", result.data)
        self.assertIn("cut_list", result.data)
        self.assertIn("manufacturing_package", result.data)
        self.assertIn("metadata", result.data)

    def test_default_specification_produces_manufacturing_data(self):
        svc = ManufacturingApplicationService()
        with patch.object(
            mfg_svc_module,
            "build_base_cabinet_manufacturing_outputs_entry",
            return_value=_FAKE_MANUFACTURING_RESULT,
        ):
            result = svc.execute()
        self.assertTrue(result.success)
        entry = result.data["manufacturing_outputs"]
        self.assertIsInstance(entry, BaseCabinetManufacturingOutputsEntryResult)
        self.assertIsNotNone(entry.cut_list)
        self.assertIsNotNone(entry.manufacturing_package)

    def test_no_fake_panel_count_or_fixed_area_in_code(self):
        """Only code lines are checked; comments are ignored."""
        code = _source_lines_without_comments(mfg_svc_module)
        self.assertNotIn("panel_count", code.lower())
        self.assertNotIn("total_area", code.lower())
        self.assertNotIn("fake", code.lower())
        self.assertNotIn("mock", code.lower())

    def test_no_new_engines_imported(self):
        source = inspect.getsource(mfg_svc_module)
        self.assertIn("build_base_cabinet_manufacturing_outputs_entry", source)
        self.assertNotIn("ManufacturingCostPipelineBuilder", source)
        self.assertNotIn("ManufacturingCommercialPipelineBuilder", source)


# ---------------------------------------------------------------------------
# ProjectApplicationService
# ---------------------------------------------------------------------------

class TestProjectApplicationServiceContract(unittest.TestCase):
    """Must call the real product workflow entry point."""

    def test_calls_build_base_cabinet_product_workflow(self):
        """Verify delegation: service calls the real product workflow."""
        svc = ProjectApplicationService()
        spec = BaseCabinetSpecification()
        fake_result = BaseCabinetProductResult(
            specification=spec,
            diagnostics=(),
        )

        with patch.object(
            project_svc_module,
            "build_base_cabinet_product_workflow",
            return_value=fake_result,
        ) as spy:
            result = svc.execute(
                specification=spec, create_document=False
            )

        self.assertTrue(result.success)
        spy.assert_called_once()
        # create_document=False, so document_name is None and
        # ProjectService is never imported (lazy).
        self.assertIsNone(result.data["document_name"])

    def test_returns_application_service_result(self):
        svc = ProjectApplicationService()
        with patch.object(
            project_svc_module,
            "build_base_cabinet_product_workflow",
            return_value=_FAKE_PROJECT_RESULT,
        ):
            result = svc.execute(
                specification=BaseCabinetSpecification(), create_document=False
            )
        self.assertIsInstance(result, ApplicationServiceResult)
        self.assertIn("project_result", result.data)
        self.assertIn("specification", result.data)

    def test_contains_diagnostics_from_underlying_workflow(self):
        svc = ProjectApplicationService()
        with patch.object(
            project_svc_module,
            "build_base_cabinet_product_workflow",
            return_value=_FAKE_PROJECT_RESULT,
        ):
            result = svc.execute(
                specification=BaseCabinetSpecification(), create_document=False
            )
        self.assertIsInstance(result.diagnostics, tuple)

    def test_no_mock_fallback_in_code(self):
        code = _source_lines_without_comments(project_svc_module)
        self.assertNotIn("mock", code.lower())
        self.assertNotIn("REAL_ENGINE_AVAILABLE", code)


# ---------------------------------------------------------------------------
# Cross-cutting: no application service introduces mock/fake logic
# ---------------------------------------------------------------------------

class TestNoArchitecturalDrift(unittest.TestCase):
    """Guards against the most common Manus-code anti-patterns."""

    ALL_SERVICE_MODULES = [
        project_svc_module,
        eng_svc_module,
        mfg_svc_module,
    ]

    def test_no_real_engine_available_guard(self):
        for mod in self.ALL_SERVICE_MODULES:
            code = _source_lines_without_comments(mod)
            self.assertNotIn(
                "REAL_ENGINE_AVAILABLE", code,
                f"{mod.__name__} uses forbidden REAL_ENGINE_AVAILABLE guard",
            )

    def test_no_mock_values(self):
        for mod in self.ALL_SERVICE_MODULES:
            code = _source_lines_without_comments(mod)
            self.assertNotIn(
                "fake", code.lower(),
                f"{mod.__name__} contains 'fake' (possible mock value)",
            )

    def test_no_new_engine_imports(self):
        """None of the application services import or reference *new* engines."""
        for mod in self.ALL_SERVICE_MODULES:
            source = inspect.getsource(mod)
            self.assertNotIn("engine.CabinetBuilder", source)
            self.assertNotIn("engine.GeometryEngine", source)

    def test_each_service_return_value_is_stable_dataclass(self):
        """Every service returns an ApplicationServiceResult."""
        for svc_class in [
            ProjectApplicationService,
            EngineeringApplicationService,
            ManufacturingApplicationService,
        ]:
            svc = svc_class()
            spec = BaseCabinetSpecification()
            # Engineering needs CabinetBuilder; Manufacturing needs its
            # entry point patched; Project needs its entry point patched.
            if svc_class is EngineeringApplicationService:
                cm = patch.object(
                    _eng_entry_module, "CabinetBuilder", new=FakeCabinetBuilder,
                )
            elif svc_class is ManufacturingApplicationService:
                cm = patch.object(
                    mfg_svc_module,
                    "build_base_cabinet_manufacturing_outputs_entry",
                    return_value=_FAKE_MANUFACTURING_RESULT,
                )
            else:
                cm = patch.object(
                    project_svc_module,
                    "build_base_cabinet_product_workflow",
                    return_value=_FAKE_PROJECT_RESULT,
                )
            with cm:
                result = svc.execute(
                    specification=spec,
                    create_document=not issubclass(
                        svc_class, ProjectApplicationService
                    ),
                )
            self.assertIsInstance(
                result, ApplicationServiceResult,
                f"{svc_class.__name__}.execute() did not return ApplicationServiceResult",
            )
            self.assertIsInstance(result.success, bool)
            self.assertIsInstance(result.errors, tuple)
            self.assertIsInstance(result.diagnostics, tuple)


if __name__ == "__main__":
    unittest.main()
