import ast
import inspect
import unittest
from typing import get_type_hints
from unittest.mock import patch

import domain.base_cabinet_engineering_entry as base_entry_module
import domain.wall_cabinet_engineering_entry as wall_entry_module
from domain.base_cabinet_engineering_entry import (
    attach_base_cabinet_engineering_models,
    build_base_cabinet_engineering_cabinet,
)
from domain.base_cabinet_engineering_model import BaseCabinetEngineeringModel
from domain.base_cabinet_specification import BaseCabinetSpecification
from domain.construction_resolver import ConstructionResolver
from domain.wall_cabinet_engineering_model import WallCabinetEngineeringModel
from domain.wall_cabinet_engineering_entry import (
    WallCabinetEngineeringEntryResult,
    build_wall_cabinet_engineering_cabinet,
)
from domain.wall_cabinet_specification import WallCabinetSpecification
from engine.cabinet import Cabinet


class FakeCabinetBuilder:
    instances_created = 0
    build_calls = 0
    last_cabinet = None

    def __init__(self):
        type(self).instances_created += 1
        self.scene_graph = object()

    def build(self, cabinet):
        type(self).build_calls += 1
        type(self).last_cabinet = cabinet
        cabinet.graph = self.scene_graph
        cabinet.scene_graph = self.scene_graph


def _imported_modules(module):
    source = inspect.getsource(module)
    tree = ast.parse(source)
    imported_modules = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.append(node.module)
    return {module.lower() for module in imported_modules}


class TestEngineeringEntryOrchestrationContract(unittest.TestCase):
    def test_engineering_entry_accepts_only_engineering_input_contracts(self):
        base_sig = inspect.signature(build_base_cabinet_engineering_cabinet)
        wall_sig = inspect.signature(build_wall_cabinet_engineering_cabinet)

        self.assertEqual(list(base_sig.parameters), ["specification"])
        self.assertEqual(list(wall_sig.parameters), ["specification"])
        self.assertIs(
            get_type_hints(build_base_cabinet_engineering_cabinet)["specification"],
            BaseCabinetSpecification,
        )
        self.assertIs(
            get_type_hints(build_wall_cabinet_engineering_cabinet)["specification"],
            WallCabinetSpecification,
        )

    def test_engineering_entry_delegates_construction_generation_to_resolver(self):
        FakeCabinetBuilder.instances_created = 0
        FakeCabinetBuilder.build_calls = 0
        FakeCabinetBuilder.last_cabinet = None

        with patch.object(
            base_entry_module,
            "CabinetBuilder",
            new=FakeCabinetBuilder,
        ), patch.object(
            ConstructionResolver,
            "resolve",
            wraps=ConstructionResolver.resolve,
        ) as resolve_spy:
            cabinet = build_base_cabinet_engineering_cabinet(
                BaseCabinetSpecification()
            )

        self.assertIsInstance(cabinet, Cabinet)
        self.assertEqual(resolve_spy.call_count, 1)
        self.assertEqual(FakeCabinetBuilder.instances_created, 1)
        self.assertEqual(FakeCabinetBuilder.build_calls, 1)
        self.assertIsInstance(cabinet.construction_model, object)
        self.assertIsInstance(cabinet.engineering_model, BaseCabinetEngineeringModel)

    def test_engineering_entry_does_not_perform_downstream_work(self):
        FakeCabinetBuilder.instances_created = 0
        FakeCabinetBuilder.build_calls = 0
        FakeCabinetBuilder.last_cabinet = None

        with patch.object(
            base_entry_module,
            "CabinetBuilder",
            new=FakeCabinetBuilder,
        ):
            cabinet = build_base_cabinet_engineering_cabinet(
                BaseCabinetSpecification()
            )

        self.assertIsInstance(cabinet, Cabinet)
        self.assertIsNotNone(getattr(cabinet, "graph", None))
        self.assertIs(getattr(cabinet, "graph", None), getattr(cabinet, "scene_graph", None))

        module_imports = _imported_modules(base_entry_module)
        self.assertIn("engine.cabinet_builder", module_imports)
        for forbidden in (
            "manufacturing",
            "commercial",
            "cost",
            "scene_graph",
            "exporters",
            "ui",
            "product_configuration",
            "product_family",
        ):
            self.assertFalse(
                any(
                    module == forbidden or module.startswith(f"{forbidden}.")
                    for module in module_imports
                ),
                msg=f"unexpected import token {forbidden!r} found in {sorted(module_imports)!r}",
            )

    def test_engineering_entry_remains_family_local_and_does_not_classify_product_family(self):
        module_imports = _imported_modules(base_entry_module)
        self.assertFalse(any("product_configuration_family_classifier" in module for module in module_imports))
        self.assertFalse(any("product_configuration" in module for module in module_imports))

    def test_engineering_entry_produces_engineering_and_construction_evidence_only(self):
        FakeCabinetBuilder.instances_created = 0
        FakeCabinetBuilder.build_calls = 0
        FakeCabinetBuilder.last_cabinet = None

        with patch.object(
            base_entry_module,
            "CabinetBuilder",
            new=FakeCabinetBuilder,
        ):
            cabinet = build_base_cabinet_engineering_cabinet(
                BaseCabinetSpecification()
            )

        self.assertIsNotNone(cabinet.construction_model)
        self.assertIsNotNone(cabinet.engineering_model)
        self.assertEqual(FakeCabinetBuilder.build_calls, 1)

    def test_preserves_current_base_cabinet_executable_behavior(self):
        FakeCabinetBuilder.instances_created = 0
        FakeCabinetBuilder.build_calls = 0
        FakeCabinetBuilder.last_cabinet = None

        with patch.object(
            base_entry_module,
            "CabinetBuilder",
            new=FakeCabinetBuilder,
        ):
            cabinet = build_base_cabinet_engineering_cabinet(
                BaseCabinetSpecification()
            )

        self.assertIsInstance(cabinet, Cabinet)
        self.assertIsNotNone(cabinet.construction_model)
        self.assertIsNotNone(cabinet.engineering_model)
        self.assertEqual(FakeCabinetBuilder.instances_created, 1)
        self.assertEqual(FakeCabinetBuilder.build_calls, 1)

    def test_wall_cabinet_engineering_entry_remains_descriptive_and_non_executable(self):
        result = build_wall_cabinet_engineering_cabinet(WallCabinetSpecification())

        self.assertIsInstance(result, WallCabinetEngineeringEntryResult)
        self.assertIsInstance(result.engineering_model, WallCabinetEngineeringModel)
        self.assertFalse(result.executable_geometry)
        self.assertIsNone(result.cabinet)
        self.assertIn("does not yet produce geometry", result.reason.lower())
        self.assertEqual(result.intent.mounting_type, "wall")
        self.assertEqual(result.intent.support_strategy, "wall_mounted")
        self.assertEqual(result.engineering_model.mounting_type, "wall")
        self.assertEqual(result.engineering_model.support_strategy, "wall_mounted")

    def test_engineering_entry_imports_only_expected_engineering_domain_modules(self):
        base_imports = _imported_modules(base_entry_module)
        wall_imports = _imported_modules(wall_entry_module)

        for forbidden in (
            "manufacturing",
            "commercial",
            "cost",
            "scene_graph",
            "exporters",
            "ui",
        ):
            self.assertFalse(
                any(
                    module == forbidden or module.startswith(f"{forbidden}.")
                    for module in base_imports
                ),
                msg=f"unexpected import token {forbidden!r} found in {sorted(base_imports)!r}",
            )

        for forbidden in (
            "manufacturing",
            "commercial",
            "cost",
            "scene_graph",
            "exporters",
            "ui",
            "application",
            "productfamily",
            "product_configuration",
        ):
            self.assertFalse(
                any(
                    module == forbidden or module.startswith(f"{forbidden}.")
                    for module in wall_imports
                ),
                msg=f"unexpected import token {forbidden!r} found in {sorted(wall_imports)!r}",
            )


if __name__ == "__main__":
    unittest.main()
