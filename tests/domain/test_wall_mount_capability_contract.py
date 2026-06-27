import inspect
import unittest
from dataclasses import asdict, fields, is_dataclass

import domain.wall_mount_capability as wall_mount_module
from domain.wall_mount_capability import (
    WallMountCapabilityResult,
    WallMountCapabilitySpecification,
    WallMountCapabilityValidation,
)


class TestWallMountCapabilityContract(unittest.TestCase):
    def test_specification_dataclass(self):
        self.assertTrue(is_dataclass(WallMountCapabilitySpecification))
        self.assertEqual(
            [field.name for field in fields(WallMountCapabilitySpecification)],
            [
                "mounting_type",
                "wall_type",
                "suspension_hardware_family",
                "required_clearance_mm",
                "max_load_kg",
                "installation_method",
            ],
        )

    def test_validation_dataclass(self):
        self.assertTrue(is_dataclass(WallMountCapabilityValidation))
        self.assertEqual(
            [field.name for field in fields(WallMountCapabilityValidation)],
            [
                "is_mounting_supported",
                "is_load_within_limit",
                "has_required_clearance",
                "diagnostics",
                "warnings",
            ],
        )

    def test_result_dataclass(self):
        self.assertTrue(is_dataclass(WallMountCapabilityResult))
        self.assertEqual(
            [field.name for field in fields(WallMountCapabilityResult)],
            [
                "specification",
                "validation",
                "suspension_hardware",
                "load_constraints",
                "clearance_summary",
                "diagnostics",
                "metadata",
            ],
        )

    def test_frozen(self):
        result = WallMountCapabilityResult()

        with self.assertRaises((AttributeError, TypeError)):
            result.metadata = {}

    def test_default_values(self):
        specification = WallMountCapabilitySpecification()
        validation = WallMountCapabilityValidation()
        result = WallMountCapabilityResult()

        self.assertIsNone(specification.mounting_type)
        self.assertIsNone(specification.wall_type)
        self.assertIsNone(specification.suspension_hardware_family)
        self.assertIsNone(specification.required_clearance_mm)
        self.assertIsNone(specification.max_load_kg)
        self.assertIsNone(specification.installation_method)
        self.assertIsNone(validation.is_mounting_supported)
        self.assertIsNone(validation.is_load_within_limit)
        self.assertIsNone(validation.has_required_clearance)
        self.assertEqual(validation.diagnostics, ())
        self.assertEqual(validation.warnings, ())
        self.assertIsNone(result.specification)
        self.assertIsNone(result.validation)
        self.assertIsNone(result.suspension_hardware)
        self.assertIsNone(result.load_constraints)
        self.assertIsNone(result.clearance_summary)
        self.assertEqual(result.diagnostics, ())
        self.assertEqual(result.metadata, {})

    def test_serialization_friendliness_with_asdict(self):
        specification = WallMountCapabilitySpecification(
            mounting_type="rail",
            wall_type="concrete",
            suspension_hardware_family="HEAVY_DUTY",
            required_clearance_mm=25,
            max_load_kg=80,
            installation_method="anchor",
        )
        validation = WallMountCapabilityValidation(
            is_mounting_supported=True,
            is_load_within_limit=True,
            has_required_clearance=True,
            diagnostics=("ok",),
            warnings=("check wall plugs",),
        )
        result = WallMountCapabilityResult(
            specification=specification,
            validation=validation,
            suspension_hardware={"family": "HEAVY_DUTY"},
            load_constraints={"max_load_kg": 80},
            clearance_summary={"required_clearance_mm": 25},
            diagnostics=("warning",),
            metadata={"source": "wall-mount"},
        )

        data = asdict(result)

        self.assertEqual(data["specification"]["mounting_type"], "rail")
        self.assertEqual(data["validation"]["is_mounting_supported"], True)
        self.assertEqual(data["suspension_hardware"], {"family": "HEAVY_DUTY"})
        self.assertEqual(data["load_constraints"], {"max_load_kg": 80})
        self.assertEqual(data["clearance_summary"], {"required_clearance_mm": 25})
        self.assertEqual(data["diagnostics"], ("warning",))
        self.assertEqual(data["metadata"], {"source": "wall-mount"})

    def test_equality(self):
        first = WallMountCapabilityResult(
            specification=WallMountCapabilitySpecification(mounting_type="rail"),
            validation=WallMountCapabilityValidation(is_mounting_supported=True),
            suspension_hardware="hardware",
            load_constraints="constraints",
            clearance_summary="clearance",
            diagnostics=("d1",),
            metadata={"source": "wall"},
        )
        second = WallMountCapabilityResult(
            specification=WallMountCapabilitySpecification(mounting_type="rail"),
            validation=WallMountCapabilityValidation(is_mounting_supported=True),
            suspension_hardware="hardware",
            load_constraints="constraints",
            clearance_summary="clearance",
            diagnostics=("d1",),
            metadata={"source": "wall"},
        )

        self.assertEqual(first, second)

    def test_metadata_default_is_not_shared(self):
        first = WallMountCapabilityResult()
        second = WallMountCapabilityResult()

        first.metadata["source"] = "wall-mount"

        self.assertEqual(second.metadata, {})
        self.assertIsNot(first.metadata, second.metadata)

    def test_diagnostics_default_is_immutable_tuple(self):
        result = WallMountCapabilityResult()

        self.assertIsInstance(result.diagnostics, tuple)
        self.assertEqual(result.diagnostics, ())
        self.assertFalse(hasattr(result.diagnostics, "append"))

    def test_no_runtime_methods(self):
        result = WallMountCapabilityResult()

        self.assertFalse(hasattr(result, "build"))
        self.assertFalse(hasattr(result, "run"))
        self.assertFalse(hasattr(result, "execute"))

    def test_contract_has_no_business_logic(self):
        public_callable_names = []
        for name in dir(WallMountCapabilitySpecification):
            if name.startswith("_"):
                continue
            value = getattr(WallMountCapabilitySpecification, name)
            if callable(value):
                public_callable_names.append(name)

        for name in dir(WallMountCapabilityValidation):
            if name.startswith("_"):
                continue
            value = getattr(WallMountCapabilityValidation, name)
            if callable(value):
                public_callable_names.append(name)

        for name in dir(WallMountCapabilityResult):
            if name.startswith("_"):
                continue
            value = getattr(WallMountCapabilityResult, name)
            if callable(value):
                public_callable_names.append(name)

        generated_methods = {
            "__init__",
            "__repr__",
            "__eq__",
            "__hash__",
            "__match_args__",
        }
        self.assertTrue(
            all(
                name in generated_methods or name.startswith("__")
                for name in public_callable_names
            )
        )

        for cls in (
            WallMountCapabilitySpecification,
            WallMountCapabilityValidation,
            WallMountCapabilityResult,
        ):
            self.assertFalse(
                any(isinstance(value, property) for value in vars(cls).values())
            )
            self.assertFalse(
                any(isinstance(value, staticmethod) for value in vars(cls).values())
            )
            self.assertFalse(
                any(isinstance(value, classmethod) for value in vars(cls).values())
            )

    def test_no_freecad_import_in_source(self):
        source = inspect.getsource(wall_mount_module)
        self.assertNotIn("FreeCAD", source)

    def test_no_runtime_import_in_source(self):
        source = inspect.getsource(wall_mount_module).lower()
        self.assertNotIn("from manufacturing", source)
        self.assertNotIn("import manufacturing", source)
        self.assertNotIn("from cost_intelligence", source)
        self.assertNotIn("import cost_intelligence", source)
        self.assertNotIn("from domain.base_cabinet_product_workflow", source)
        self.assertNotIn("basecabinetproductworkflow", source)


if __name__ == "__main__":
    unittest.main()
