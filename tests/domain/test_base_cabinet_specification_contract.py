import unittest
from dataclasses import asdict, fields, is_dataclass

from domain.base_cabinet_specification import BaseCabinetSpecification


class TestBaseCabinetSpecificationContract(unittest.TestCase):
    def test_dataclass(self):
        spec = BaseCabinetSpecification()
        self.assertTrue(is_dataclass(spec))

    def test_frozen(self):
        spec = BaseCabinetSpecification()
        with self.assertRaises((AttributeError, TypeError)):
            spec.width_mm = 700.0

    def test_default_values(self):
        spec = BaseCabinetSpecification()
        self.assertEqual(spec.width_mm, 600.0)
        self.assertEqual(spec.height_mm, 720.0)
        self.assertEqual(spec.depth_mm, 580.0)
        self.assertEqual(spec.door_count, 2)
        self.assertEqual(spec.shelf_count, 1)
        self.assertTrue(spec.has_back_panel)
        self.assertTrue(spec.edge_banding_required)
        self.assertTrue(spec.toe_kick_required)
        self.assertEqual(spec.hinge_family, "STANDARD_110")
        self.assertEqual(spec.drawer_family, "NONE")

    def test_serialization_with_asdict(self):
        spec = BaseCabinetSpecification()
        data = asdict(spec)
        self.assertEqual(data["width_mm"], 600.0)
        self.assertEqual(data["hinge_family"], "STANDARD_110")
        self.assertEqual(set(data.keys()), {field.name for field in fields(BaseCabinetSpecification)})

    def test_equality(self):
        self.assertEqual(BaseCabinetSpecification(), BaseCabinetSpecification())
        self.assertNotEqual(
            BaseCabinetSpecification(),
            BaseCabinetSpecification(width_mm=700.0),
        )

    def test_no_runtime_methods(self):
        spec = BaseCabinetSpecification()
        for method_name in ("run", "execute", "build", "compile", "schedule"):
            self.assertFalse(hasattr(spec, method_name))


if __name__ == "__main__":
    unittest.main()
