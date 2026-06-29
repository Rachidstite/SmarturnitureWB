import inspect
import ast
import unittest
from dataclasses import asdict, fields, is_dataclass

import domain.wall_mount_rules as wall_mount_rules_module
from domain.wall_mount_rules import (
    WallMountAnchorCompatibilityRule,
    WallMountClearanceRule,
    WallMountHardwareCompatibilityRule,
    WallMountLoadRule,
    WallMountRetentionRule,
)


class TestWallMountRulesContract(unittest.TestCase):
    def _assert_rule_dataclass(self, cls, expected_fields):
        self.assertTrue(is_dataclass(cls))
        self.assertEqual([field.name for field in fields(cls)], expected_fields)

    def test_dataclasses_exist(self):
        self._assert_rule_dataclass(
            WallMountLoadRule,
            [
                "rule_id",
                "business_reason",
                "engineering_reason",
                "manufacturing_impact",
                "validation_target",
                "severity",
                "metadata",
            ],
        )
        self._assert_rule_dataclass(
            WallMountAnchorCompatibilityRule,
            [
                "rule_id",
                "business_reason",
                "engineering_reason",
                "manufacturing_impact",
                "validation_target",
                "severity",
                "metadata",
            ],
        )
        self._assert_rule_dataclass(
            WallMountClearanceRule,
            [
                "rule_id",
                "business_reason",
                "engineering_reason",
                "manufacturing_impact",
                "validation_target",
                "severity",
                "metadata",
            ],
        )
        self._assert_rule_dataclass(
            WallMountRetentionRule,
            [
                "rule_id",
                "business_reason",
                "engineering_reason",
                "manufacturing_impact",
                "validation_target",
                "severity",
                "metadata",
            ],
        )
        self._assert_rule_dataclass(
            WallMountHardwareCompatibilityRule,
            [
                "rule_id",
                "business_reason",
                "engineering_reason",
                "manufacturing_impact",
                "validation_target",
                "severity",
                "metadata",
            ],
        )

    def test_immutable_frozen(self):
        rule = WallMountLoadRule()
        with self.assertRaises((AttributeError, TypeError)):
            rule.rule_id = "wall-load"

    def test_serialization_friendly(self):
        rule = WallMountAnchorCompatibilityRule(
            rule_id="anchor.compatibility",
            business_reason="Use compatible anchors",
            engineering_reason="Wall substrate compatibility matters",
            manufacturing_impact="Hardware kit selection",
            validation_target="Anchor compatibility",
            severity="HIGH",
            metadata={"wall_type": "concrete"},
        )

        data = asdict(rule)

        self.assertEqual(data["rule_id"], "anchor.compatibility")
        self.assertEqual(data["business_reason"], "Use compatible anchors")
        self.assertEqual(data["engineering_reason"], "Wall substrate compatibility matters")
        self.assertEqual(data["manufacturing_impact"], "Hardware kit selection")
        self.assertEqual(data["validation_target"], "Anchor compatibility")
        self.assertEqual(data["severity"], "HIGH")
        self.assertEqual(data["metadata"], {"wall_type": "concrete"})

    def test_metadata_default_is_not_shared(self):
        first = WallMountClearanceRule()
        second = WallMountClearanceRule()

        first.metadata["required_clearance_mm"] = 25

        self.assertEqual(second.metadata, {})
        self.assertIsNot(first.metadata, second.metadata)

    def test_no_runtime_methods(self):
        rule = WallMountRetentionRule()
        self.assertFalse(hasattr(rule, "build"))
        self.assertFalse(hasattr(rule, "run"))
        self.assertFalse(hasattr(rule, "execute"))

    def test_no_business_logic(self):
        for cls in (
            WallMountLoadRule,
            WallMountAnchorCompatibilityRule,
            WallMountClearanceRule,
            WallMountRetentionRule,
            WallMountHardwareCompatibilityRule,
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

    def test_no_runtime_imports(self):
        source = inspect.getsource(wall_mount_rules_module)
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
        self.assertFalse(any("basecabinet" in module for module in lowered))
        self.assertFalse(any("workflow" in module for module in lowered))


if __name__ == "__main__":
    unittest.main()
