import inspect
import unittest
from unittest.mock import patch

import domain.base_cabinet_engineering_entry as engineering_entry_module
from domain.base_cabinet_engineering_entry import (
    build_base_cabinet_engineering_cabinet,
)
from domain.base_cabinet_engineering_model import BaseCabinetEngineeringModel
from domain.base_cabinet_specification import BaseCabinetSpecification
from domain.base_cabinet_specification_adapter import (
    BaseCabinetSpecificationAdapter,
)
from engine.cabinet import Cabinet


class FakeCabinetBuilder:
    instances_created = 0
    build_calls = 0
    last_cabinet = None

    def __init__(self):
        type(self).instances_created += 1

    def build(self, cabinet):
        type(self).build_calls += 1
        type(self).last_cabinet = cabinet


class TestBaseCabinetEngineeringEntryContract(unittest.TestCase):
    def test_accepts_base_cabinet_specification(self):
        FakeCabinetBuilder.instances_created = 0
        FakeCabinetBuilder.build_calls = 0
        FakeCabinetBuilder.last_cabinet = None
        with patch.object(
            engineering_entry_module,
            "ConstructionResolver",
            wraps=engineering_entry_module.ConstructionResolver,
        ) as resolver_cls, patch.object(
            engineering_entry_module,
            "BaseCabinetEngineeringModelBuilder",
            wraps=engineering_entry_module.BaseCabinetEngineeringModelBuilder,
        ) as engineering_model_cls, patch.object(
            engineering_entry_module,
            "CabinetBuilder",
            new=FakeCabinetBuilder,
        ):
            cabinet = build_base_cabinet_engineering_cabinet(
                BaseCabinetSpecification()
            )

        self.assertIsInstance(cabinet, Cabinet)
        self.assertIsNotNone(cabinet.construction_model)
        self.assertIsInstance(cabinet.engineering_model, BaseCabinetEngineeringModel)
        resolver_cls.resolve.assert_called_once()
        engineering_model_cls.build.assert_called_once()
        self.assertEqual(FakeCabinetBuilder.instances_created, 1)
        self.assertEqual(FakeCabinetBuilder.build_calls, 1)

    def test_uses_adapter(self):
        FakeCabinetBuilder.instances_created = 0
        FakeCabinetBuilder.build_calls = 0
        FakeCabinetBuilder.last_cabinet = None
        with patch.object(
            BaseCabinetSpecificationAdapter,
            "adapt",
            wraps=BaseCabinetSpecificationAdapter.adapt,
        ) as adapt_spy, patch.object(
            engineering_entry_module,
            "ConstructionResolver",
            wraps=engineering_entry_module.ConstructionResolver,
        ) as resolver_cls, patch.object(
            engineering_entry_module,
            "BaseCabinetEngineeringModelBuilder",
            wraps=engineering_entry_module.BaseCabinetEngineeringModelBuilder,
        ) as engineering_model_cls, patch.object(
            engineering_entry_module,
            "CabinetBuilder",
            new=FakeCabinetBuilder,
        ):
            build_base_cabinet_engineering_cabinet(BaseCabinetSpecification())

        adapt_spy.assert_called_once()
        resolver_cls.resolve.assert_called_once()
        engineering_model_cls.build.assert_called_once()
        self.assertEqual(FakeCabinetBuilder.instances_created, 1)
        self.assertEqual(FakeCabinetBuilder.build_calls, 1)

    def test_delegates_to_existing_cabinet_builder(self):
        FakeCabinetBuilder.instances_created = 0
        FakeCabinetBuilder.build_calls = 0
        FakeCabinetBuilder.last_cabinet = None
        with patch.object(
            engineering_entry_module,
            "ConstructionResolver",
            wraps=engineering_entry_module.ConstructionResolver,
        ) as resolver_cls, patch.object(
            engineering_entry_module,
            "BaseCabinetEngineeringModelBuilder",
            wraps=engineering_entry_module.BaseCabinetEngineeringModelBuilder,
        ) as engineering_model_cls, patch.object(
            engineering_entry_module,
            "CabinetBuilder",
            new=FakeCabinetBuilder,
        ):
            build_base_cabinet_engineering_cabinet(BaseCabinetSpecification())

        resolver_cls.resolve.assert_called_once()
        engineering_model_cls.build.assert_called_once()
        self.assertEqual(FakeCabinetBuilder.instances_created, 1)
        self.assertEqual(FakeCabinetBuilder.build_calls, 1)
        self.assertIsInstance(FakeCabinetBuilder.last_cabinet, Cabinet)
        self.assertIsNotNone(FakeCabinetBuilder.last_cabinet.construction_model)
        self.assertIsInstance(
            FakeCabinetBuilder.last_cabinet.engineering_model,
            BaseCabinetEngineeringModel,
        )

    def test_returns_existing_cabinet_type(self):
        FakeCabinetBuilder.instances_created = 0
        FakeCabinetBuilder.build_calls = 0
        FakeCabinetBuilder.last_cabinet = None
        with patch.object(
            engineering_entry_module,
            "ConstructionResolver",
            wraps=engineering_entry_module.ConstructionResolver,
        ) as resolver_cls, patch.object(
            engineering_entry_module,
            "BaseCabinetEngineeringModelBuilder",
            wraps=engineering_entry_module.BaseCabinetEngineeringModelBuilder,
        ) as engineering_model_cls, patch.object(
            engineering_entry_module,
            "CabinetBuilder",
            new=FakeCabinetBuilder,
        ):
            cabinet = build_base_cabinet_engineering_cabinet(
                BaseCabinetSpecification()
            )

        resolver_cls.resolve.assert_called_once()
        engineering_model_cls.build.assert_called_once()
        self.assertIsInstance(cabinet, Cabinet)

    def test_no_freecad_import_in_source(self):
        source = inspect.getsource(engineering_entry_module)
        self.assertNotIn("FreeCAD", source)

    def test_no_runtime_execution_methods(self):
        source = inspect.getsource(engineering_entry_module)
        self.assertNotIn("def run", source)
        self.assertNotIn("def execute", source)

    def test_no_runtime_imports_in_source(self):
        source = inspect.getsource(engineering_entry_module)
        self.assertNotIn("manufacturing", source.lower())
        self.assertNotIn("validation", source.lower())


if __name__ == "__main__":
    unittest.main()
