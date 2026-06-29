import ast
import inspect
import unittest
from enum import Enum

import domain.wall_mount_vocabulary as wall_mount_vocab_module
from domain.wall_mount_vocabulary import (
    AnchorType,
    ClearanceType,
    FailureMode,
    LoadCategory,
    MountingType,
    SuspensionHardwareFamily,
    WallType,
)


class TestWallMountVocabularyContract(unittest.TestCase):
    def test_enums_exist(self):
        for cls in (
            MountingType,
            WallType,
            AnchorType,
            SuspensionHardwareFamily,
            LoadCategory,
            ClearanceType,
            FailureMode,
        ):
            self.assertTrue(issubclass(cls, Enum))

    def test_stable_values(self):
        self.assertEqual(MountingType.CONCEALED_RAIL.value, "CONCEALED_RAIL")
        self.assertEqual(MountingType.FRENCH_CLEAT.value, "FRENCH_CLEAT")
        self.assertEqual(WallType.CONCRETE.value, "CONCRETE")
        self.assertEqual(WallType.PLASTERBOARD_OVER_STUD.value, "PLASTERBOARD_OVER_STUD")
        self.assertEqual(AnchorType.CHEMICAL_ANCHOR.value, "CHEMICAL_ANCHOR")
        self.assertEqual(SuspensionHardwareFamily.WALL_RAIL.value, "WALL_RAIL")
        self.assertEqual(LoadCategory.STATIC_DISTRIBUTED.value, "STATIC_DISTRIBUTED")
        self.assertEqual(ClearanceType.TOP_INSTALLATION.value, "TOP_INSTALLATION")
        self.assertEqual(FailureMode.ANCHOR_PULL_OUT.value, "ANCHOR_PULL_OUT")

    def test_serialization_friendly(self):
        data = {
            "mounting_type": MountingType.CONCEALED_RAIL.value,
            "wall_type": WallType.CONCRETE.value,
            "anchor_type": AnchorType.EXPANSION_ANCHOR.value,
            "suspension_hardware_family": SuspensionHardwareFamily.WALL_RAIL.value,
            "load_category": LoadCategory.STATIC_DISTRIBUTED.value,
            "clearance_type": ClearanceType.REAR_SERVICE.value,
            "failure_mode": FailureMode.ANCHOR_SHEAR.value,
        }

        self.assertEqual(data["mounting_type"], "CONCEALED_RAIL")
        self.assertEqual(data["wall_type"], "CONCRETE")
        self.assertEqual(data["anchor_type"], "EXPANSION_ANCHOR")
        self.assertEqual(data["suspension_hardware_family"], "WALL_RAIL")
        self.assertEqual(data["load_category"], "STATIC_DISTRIBUTED")
        self.assertEqual(data["clearance_type"], "REAR_SERVICE")
        self.assertEqual(data["failure_mode"], "ANCHOR_SHEAR")

    def test_no_runtime_imports(self):
        source = inspect.getsource(wall_mount_vocab_module)
        tree = ast.parse(source)
        imported_modules = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_modules.append(node.module)

        lowered = {module.lower() for module in imported_modules}
        self.assertFalse(any("freecad" in module for module in lowered))
        self.assertFalse(any("manufacturing" in module for module in lowered))
        self.assertFalse(any("cost_intelligence" in module for module in lowered))
        self.assertFalse(any("workflow" in module for module in lowered))
        self.assertFalse(any("domain.base_cabinet" in module for module in lowered))

    def test_no_business_logic(self):
        source = inspect.getsource(wall_mount_vocab_module)
        tree = ast.parse(source)
        function_defs = [
            node
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        self.assertEqual(function_defs, [])

    def test_module_has_only_vocab_and_imports(self):
        public_names = [
            name
            for name, value in vars(wall_mount_vocab_module).items()
            if not name.startswith("_") and inspect.isclass(value)
        ]
        self.assertEqual(
            public_names,
            [
                "Enum",
                "MountingType",
                "WallType",
                "AnchorType",
                "SuspensionHardwareFamily",
                "LoadCategory",
                "ClearanceType",
                "FailureMode",
            ],
        )


if __name__ == "__main__":
    unittest.main()
