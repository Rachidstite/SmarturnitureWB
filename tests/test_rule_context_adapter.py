import copy
import unittest
from types import SimpleNamespace

from domain.rules_engine import RuleContext, build_rule_context_from_params


class TestRuleContextAdapter(unittest.TestCase):

    def test_default_rule_context_remains_unchanged(self):
        context = RuleContext()

        self.assertEqual(
            context.hardware_profile["INTENT_HINGE"],
            "HINGE_BLUM_110_V1",
        )
        self.assertEqual(
            context.hardware_profile["INTENT_DRAWER_SLIDE"],
            "DRAWER_SLIDE_SOFTCLOSE_450",
        )

    def test_build_rule_context_maps_hinge_sku(self):
        params = SimpleNamespace(hinge_sku="HINGE_CUSTOM")

        context = build_rule_context_from_params(params)

        self.assertEqual(context.hardware_profile["INTENT_HINGE"], "HINGE_CUSTOM")

    def test_build_rule_context_maps_slide_sku(self):
        params = SimpleNamespace(slide_sku="SLIDE_CUSTOM")

        context = build_rule_context_from_params(params)

        self.assertEqual(
            context.hardware_profile["INTENT_DRAWER_SLIDE"],
            "SLIDE_CUSTOM",
        )

    def test_build_rule_context_maps_handle_sku(self):
        params = SimpleNamespace(handle_sku="HANDLE_CUSTOM")

        context = build_rule_context_from_params(params)

        self.assertEqual(context.hardware_profile["INTENT_HANDLE"], "HANDLE_CUSTOM")

    def test_build_rule_context_does_not_mutate_base_context(self):
        base_context = RuleContext()
        original_profile = copy.deepcopy(base_context.hardware_profile)
        params = SimpleNamespace(hinge_sku="HINGE_CUSTOM")

        context = build_rule_context_from_params(params, base_context=base_context)

        self.assertIsNot(context, base_context)
        self.assertEqual(base_context.hardware_profile, original_profile)
        self.assertEqual(context.hardware_profile["INTENT_HINGE"], "HINGE_CUSTOM")

    def test_build_rule_context_preserves_other_entries(self):
        base_context = RuleContext()
        base_context.hardware_profile["INTENT_EXTRA"] = "EXTRA_SKU"

        context = build_rule_context_from_params(
            SimpleNamespace(slide_sku="SLIDE_CUSTOM"),
            base_context=base_context,
        )

        self.assertEqual(context.hardware_profile["INTENT_EXTRA"], "EXTRA_SKU")
        self.assertEqual(
            context.hardware_profile["INTENT_DRAWER_SLIDE"],
            "SLIDE_CUSTOM",
        )

    def test_build_rule_context_works_with_missing_skus(self):
        context = build_rule_context_from_params(SimpleNamespace())

        self.assertEqual(
            context.hardware_profile["INTENT_HINGE"],
            "HINGE_BLUM_110_V1",
        )
        self.assertEqual(
            context.hardware_profile["INTENT_DRAWER_SLIDE"],
            "DRAWER_SLIDE_SOFTCLOSE_450",
        )
        self.assertEqual(
            context.hardware_profile["INTENT_CONFIRMAT_50"],
            "CONFIRMAT_50_V1",
        )


if __name__ == "__main__":
    unittest.main()
