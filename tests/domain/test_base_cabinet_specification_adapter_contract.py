import inspect
import unittest
from dataclasses import asdict, is_dataclass

import domain.base_cabinet_specification_adapter as adapter_module
from domain.base_cabinet_specification import BaseCabinetSpecification
from domain.base_cabinet_specification_adapter import (
    BaseCabinetSpecificationAdapter,
    BaseCabinetSpecificationAdapterResult,
)
from shared.contracts import CabinetParams, SectionConfig


class TestBaseCabinetSpecificationAdapterContract(unittest.TestCase):
    def test_adapter_accepts_base_cabinet_specification(self):
        specification = BaseCabinetSpecification()
        result = BaseCabinetSpecificationAdapter.adapt(specification)
        self.assertIsInstance(result, BaseCabinetSpecificationAdapterResult)
        self.assertTrue(is_dataclass(result))
        self.assertIsInstance(result.cabinet_params, CabinetParams)

    def test_cabinet_params_are_converted_to_base_cabinet_specification(self):
        params = CabinetParams(
            width=820.0,
            height=730.0,
            depth=590.0,
            base_height=90.0,
            sec_count=1,
            sec_data={
                0: type(
                    "SectionConfig",
                    (),
                    {"door_count": 3, "shelves": 2, "drawer_type": "Inset"},
                )()
            },
            hinge_sku="HINGE_SPECIAL",
        )

        spec = BaseCabinetSpecificationAdapter.from_cabinet_params(params)

        self.assertIsInstance(spec, BaseCabinetSpecification)
        self.assertEqual(spec.width_mm, 820.0)
        self.assertEqual(spec.height_mm, 730.0)
        self.assertEqual(spec.depth_mm, 590.0)
        self.assertEqual(spec.door_count, 3)
        self.assertEqual(spec.shelf_count, 2)
        self.assertTrue(spec.has_back_panel)
        self.assertTrue(spec.edge_banding_required)
        self.assertTrue(spec.toe_kick_required)
        self.assertEqual(spec.hinge_family, "HINGE_SPECIAL")
        self.assertEqual(spec.drawer_family, "Inset")

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

    def test_shelf_and_door_counts_reach_geometry_engine_input_shape(self):
        specification = BaseCabinetSpecification(
            shelf_count=4,
            door_count=3,
        )

        result = BaseCabinetSpecificationAdapter.adapt(specification)
        section = result.cabinet_params.sec_data[0]

        self.assertEqual(result.cabinet_params.sec_count, 1)
        self.assertIsInstance(section, SectionConfig)
        self.assertEqual(section.shelves, 4)
        self.assertEqual(section.door_count, 3)
        self.assertEqual(section.doors, "Inset")

    def test_zero_door_count_disables_door_generation_in_geometry_input_shape(self):
        specification = BaseCabinetSpecification(door_count=0)

        result = BaseCabinetSpecificationAdapter.adapt(specification)
        section = result.cabinet_params.sec_data[0]

        self.assertEqual(section.door_count, 0)
        self.assertEqual(section.doors, "None")

    def test_unsupported_mappings_are_not_applied_to_cabinet_params(self):
        specification = BaseCabinetSpecification(
            door_count=2,
            edge_banding_required=True,
            drawer_family="DRAWER_CUSTOM",
        )
        result = BaseCabinetSpecificationAdapter.adapt(specification)
        self.assertNotEqual(result.cabinet_params.sec_count, specification.door_count)
        self.assertNotEqual(result.cabinet_params.hw_mode, specification.edge_banding_required)
        self.assertNotEqual(result.cabinet_params.handle_sku, specification.drawer_family)

    def test_adapter_output_is_serialization_friendly(self):
        result = BaseCabinetSpecificationAdapter.adapt(BaseCabinetSpecification())
        payload = asdict(result)
        self.assertIn("cabinet_params", payload)
        self.assertIn("metadata", payload)
        self.assertEqual(payload["cabinet_params"]["width"], 600.0)
        self.assertEqual(payload["metadata"]["door_count"], 2)
        self.assertEqual(payload["metadata"]["hinge_family"], "STANDARD_110")

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
