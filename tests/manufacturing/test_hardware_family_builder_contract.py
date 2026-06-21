import unittest
from types import SimpleNamespace


class TestHardwareFamilyBuilderContract(unittest.TestCase):

    def test_hardware_intelligence_builder_prefers_spec_family_over_sku_fallback(self):
        from domain.anchors import AnchorCoordinate, EdgeRef, HardwarePlacement, MountFace
        from manufacturing.hardware_intelligence_builder import (
            HardwareIntelligenceBuilder,
        )

        class FamilyAwareRegistry:
            def get_hardware(self, sku):
                return SimpleNamespace(
                    sku=sku,
                    hardware_family="CUSTOM_FAMILY",
                    host_holes=[],
                    target_holes=[],
                )

        anchor = AnchorCoordinate(MountFace.LEFT, EdgeRef.FRONT, 0.0, 0.0)
        project = SimpleNamespace(
            placements=[
                HardwarePlacement("HOST_A", "INTENT_CUSTOM", anchor, "TARGET_A"),
            ]
        )
        context = SimpleNamespace(
            hardware_profile={
                "INTENT_CUSTOM": "CUSTOM_SKU",
            }
        )

        reports = HardwareIntelligenceBuilder(registry=FamilyAwareRegistry()).build(
            project,
            context,
        )

        self.assertEqual(len(reports), 1)
        self.assertEqual(reports[0].hardware_family, "CUSTOM_FAMILY")
        self.assertEqual(reports[0].total_hardware_items, 1)
        self.assertFalse(reports[0].requires_review)


if __name__ == "__main__":
    unittest.main()
