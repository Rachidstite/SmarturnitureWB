import inspect
import unittest
from dataclasses import asdict, is_dataclass

import domain.base_cabinet_specification_adapter as adapter_module
from domain.base_cabinet_specification import BaseCabinetSpecification
from domain.base_cabinet_specification_adapter import (
    BaseCabinetSpecificationAdapter,
    BaseCabinetSpecificationAdapterResult,
)
from shared.contracts import CabinetParams


class TestBaseCabinetSpecificationAdapterContract(unittest.TestCase):
    def test_adapter_accepts_base_cabinet_specification(self):
        specification = BaseCabinetSpecification()
        result = BaseCabinetSpecificationAdapter.adapt(specification)
        self.assertIsInstance(result, BaseCabinetSpecificationAdapterResult)
        self.assertTrue(is_dataclass(result))
        self.assertIsInstance(result.cabinet_params, CabinetParams)

    def test_width_height_depth_are_preserved(self):
        specification = BaseCabinetSpecification(
            width_mm=750.0,
            height_mm=900.0,
            depth_mm=620.0,
        )
        result = BaseCabinetSpecificationAdapter.adapt(specification)
        self.assertEqual(result.cabinet_params.width, 750.0)
        self.assertEqual(result.cabinet_params.height, 900.0)
        self.assertEqual(result.cabinet_params.depth, 620.0)

    def test_product_configuration_fields_are_preserved_in_metadata(self):
        specification = BaseCabinetSpecification(
            door_count=2,
            shelf_count=1,
            has_back_panel=True,
            edge_banding_required=True,
            toe_kick_required=True,
            hinge_family="STANDARD_110",
            drawer_family="NONE",
        )
        result = BaseCabinetSpecificationAdapter.adapt(specification)
        self.assertEqual(result.metadata["door_count"], 2)
        self.assertEqual(result.metadata["shelf_count"], 1)
        self.assertTrue(result.metadata["has_back_panel"])
        self.assertTrue(result.metadata["edge_banding_required"])
        self.assertTrue(result.metadata["toe_kick_required"])
        self.assertEqual(result.metadata["hinge_family"], "STANDARD_110")
        self.assertEqual(result.metadata["drawer_family"], "NONE")

    def test_adapter_output_is_serialization_friendly(self):
        result = BaseCabinetSpecificationAdapter.adapt(BaseCabinetSpecification())
        payload = asdict(result)
        self.assertIn("cabinet_params", payload)
        self.assertIn("metadata", payload)
        self.assertEqual(payload["cabinet_params"]["width"], 600.0)
        self.assertEqual(payload["metadata"]["cabinet_type"], "Base Cabinet")

    def test_no_runtime_build_execute_methods(self):
        self.assertFalse(hasattr(BaseCabinetSpecificationAdapter, "build"))
        self.assertFalse(hasattr(BaseCabinetSpecificationAdapter, "execute"))
        self.assertFalse(hasattr(BaseCabinetSpecificationAdapter, "run"))

    def test_no_freecad_import(self):
        source = inspect.getsource(adapter_module)
        self.assertNotIn("FreeCAD", source)

    def test_no_manufacturing_execution_import(self):
        source = inspect.getsource(adapter_module)
        self.assertNotIn("ManufacturingProductionPackage", source)
        self.assertNotIn("ProductionPackage", source)


if __name__ == "__main__":
    unittest.main()
