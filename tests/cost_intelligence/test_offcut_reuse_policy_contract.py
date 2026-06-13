import unittest
from dataclasses import fields, is_dataclass


class TestOffcutReusePolicyContract(unittest.TestCase):

    def test_offcut_reuse_policy_exists_and_is_dataclass(self):

        try:
            from cost_intelligence.offcut_reuse_policy import (
                OffcutReusePolicy,
            )
        except ImportError:
            self.fail(
                "OffcutReusePolicy does not exist"
            )

        self.assertTrue(
            is_dataclass(OffcutReusePolicy),
        )

    def test_offcut_reuse_policy_contains_required_fields(self):

        from cost_intelligence.offcut_reuse_policy import (
            OffcutReusePolicy,
        )

        field_names = {
            field.name
            for field in fields(OffcutReusePolicy)
        }

        self.assertEqual(
            field_names,
            {
                "material",
                "thickness",
                "min_width",
                "min_height",
                "min_area",
            },
        )

    def test_offcut_reuse_policy_accepts_material_thresholds(self):

        from cost_intelligence.offcut_reuse_policy import (
            OffcutReusePolicy,
        )

        policy = OffcutReusePolicy(
            material="MDF",
            thickness=18,
            min_width=150,
            min_height=150,
            min_area=22500,
        )

        self.assertEqual(policy.material, "MDF")
        self.assertEqual(policy.thickness, 18)
        self.assertEqual(policy.min_width, 150)
        self.assertEqual(policy.min_height, 150)
        self.assertEqual(policy.min_area, 22500)


if __name__ == "__main__":
    unittest.main()
