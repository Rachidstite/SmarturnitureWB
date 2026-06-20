import copy
import unittest
from types import SimpleNamespace


class TestHardwareIntelligenceBuilder(unittest.TestCase):

    def test_builder_exists(self):
        from manufacturing.hardware_intelligence_builder import (
            HardwareIntelligenceBuilder,
        )

        self.assertTrue(callable(HardwareIntelligenceBuilder().build))

    def test_builder_generates_family_reports_from_registry_specs(self):
        from domain.anchors import AnchorCoordinate, EdgeRef, HardwarePlacement, MountFace
        from manufacturing.hardware_intelligence_builder import (
            HardwareIntelligenceBuilder,
        )
        from manufacturing.hardware_intelligence_report import (
            HardwareIntelligenceReport,
        )

        anchor = AnchorCoordinate(MountFace.LEFT, EdgeRef.FRONT, 0.0, 0.0)
        project = SimpleNamespace(
            placements=[
                HardwarePlacement("HOST_A", "INTENT_MINIFIX_15", anchor, "TARGET_A"),
                HardwarePlacement("HOST_B", "INTENT_MINIFIX_15", anchor, "TARGET_B"),
                HardwarePlacement("HOST_C", "INTENT_CONFIRMAT_50", anchor, "TARGET_C"),
                HardwarePlacement("HOST_D", "INTENT_HANDLE", anchor, ""),
            ]
        )
        context = SimpleNamespace(
            hardware_profile={
                "INTENT_MINIFIX_15": "MINIFIX_15_V1",
                "INTENT_CONFIRMAT_50": "CONFIRMAT_50_V1",
                "INTENT_HANDLE": "HANDLE_128_BLACK",
            }
        )

        reports = HardwareIntelligenceBuilder().build(project, context)
        reports_by_family = {
            report.hardware_family: report
            for report in reports
        }

        self.assertEqual(set(reports_by_family), {"MINIFIX", "CONFIRMAT", "HANDLE"})
        self.assertTrue(
            all(isinstance(report, HardwareIntelligenceReport) for report in reports)
        )

        minifix = reports_by_family["MINIFIX"]
        self.assertEqual(minifix.total_hardware_items, 2)
        self.assertEqual(minifix.total_host_holes, 2)
        self.assertEqual(minifix.total_target_holes, 4)
        self.assertEqual(minifix.total_face_holes, 4)
        self.assertEqual(minifix.total_edge_holes, 2)
        self.assertFalse(minifix.requires_review)
        self.assertEqual(minifix.manufacturing_warning, "")
        self.assertEqual(minifix.recommended_action, "")

        confirmat = reports_by_family["CONFIRMAT"]
        self.assertEqual(confirmat.total_hardware_items, 1)
        self.assertEqual(confirmat.total_host_holes, 1)
        self.assertEqual(confirmat.total_target_holes, 1)
        self.assertEqual(confirmat.total_face_holes, 1)
        self.assertEqual(confirmat.total_edge_holes, 1)

        handle = reports_by_family["HANDLE"]
        self.assertEqual(handle.total_hardware_items, 1)
        self.assertEqual(handle.total_host_holes, 2)
        self.assertEqual(handle.total_target_holes, 0)
        self.assertEqual(handle.total_face_holes, 2)
        self.assertEqual(handle.total_edge_holes, 0)

    def test_builder_flags_missing_hardware_spec_for_mapped_family(self):
        from domain.anchors import AnchorCoordinate, EdgeRef, HardwarePlacement, MountFace
        from manufacturing.hardware_intelligence_builder import (
            HardwareIntelligenceBuilder,
        )

        class MissingRegistry:
            def get_hardware(self, sku):
                return None

        anchor = AnchorCoordinate(MountFace.LEFT, EdgeRef.FRONT, 0.0, 0.0)
        project = SimpleNamespace(
            placements=[
                HardwarePlacement("HOST_A", "INTENT_CONFIRMAT_50", anchor, "TARGET_A")
            ]
        )
        context = SimpleNamespace(
            hardware_profile={
                "INTENT_CONFIRMAT_50": "CONFIRMAT_50_V1",
            }
        )

        reports = HardwareIntelligenceBuilder(registry=MissingRegistry()).build(
            project,
            context,
        )

        self.assertEqual(len(reports), 1)
        self.assertEqual(reports[0].hardware_family, "CONFIRMAT")
        self.assertEqual(reports[0].total_hardware_items, 1)
        self.assertTrue(reports[0].requires_review)
        self.assertEqual(
            reports[0].manufacturing_warning,
            "Missing hardware specification for CONFIRMAT_50_V1",
        )
        self.assertEqual(
            reports[0].recommended_action,
            "Register hardware SKU in HardwareRegistry",
        )

    def test_builder_flags_missing_hardware_profile_mapping(self):
        from domain.anchors import AnchorCoordinate, EdgeRef, HardwarePlacement, MountFace
        from manufacturing.hardware_intelligence_builder import (
            HardwareIntelligenceBuilder,
        )

        anchor = AnchorCoordinate(MountFace.LEFT, EdgeRef.FRONT, 0.0, 0.0)
        project = SimpleNamespace(
            placements=[
                HardwarePlacement("HOST_A", "INTENT_MINIFIX_15", anchor, "TARGET_A")
            ]
        )
        context = SimpleNamespace(hardware_profile={})

        reports = HardwareIntelligenceBuilder().build(project, context)

        self.assertEqual(len(reports), 1)
        self.assertEqual(reports[0].hardware_family, "MINIFIX_15")
        self.assertEqual(reports[0].total_hardware_items, 1)
        self.assertEqual(reports[0].total_host_holes, 0)
        self.assertEqual(reports[0].total_target_holes, 0)
        self.assertTrue(reports[0].requires_review)
        self.assertEqual(
            reports[0].manufacturing_warning,
            "Missing hardware profile mapping for INTENT_MINIFIX_15",
        )
        self.assertEqual(
            reports[0].recommended_action,
            "Map hardware intent to SKU in RuleContext.hardware_profile",
        )

    def test_builder_returns_empty_reports_for_empty_inputs(self):
        from manufacturing.hardware_intelligence_builder import (
            HardwareIntelligenceBuilder,
        )

        builder = HardwareIntelligenceBuilder()

        self.assertEqual(
            builder.build(SimpleNamespace(placements=[]), SimpleNamespace(hardware_profile={})),
            [],
        )
        self.assertEqual(
            builder.build(SimpleNamespace(), SimpleNamespace()),
            [],
        )

    def test_builder_falls_back_to_sku_when_family_mapping_is_unknown(self):
        from domain.anchors import AnchorCoordinate, EdgeRef, HardwarePlacement, MountFace
        from manufacturing.hardware_intelligence_builder import (
            HardwareIntelligenceBuilder,
        )

        anchor = AnchorCoordinate(MountFace.LEFT, EdgeRef.FRONT, 0.0, 0.0)
        project = SimpleNamespace(
            placements=[
                HardwarePlacement("HOST_A", "INTENT_LATCH", anchor, ""),
            ]
        )
        context = SimpleNamespace(
            hardware_profile={
                "INTENT_LATCH": "TOUCH_LATCH_STANDARD",
            }
        )

        reports = HardwareIntelligenceBuilder().build(project, context)

        self.assertEqual(len(reports), 1)
        self.assertEqual(reports[0].hardware_family, "TOUCH_LATCH_STANDARD")
        self.assertEqual(reports[0].total_hardware_items, 1)
        self.assertEqual(reports[0].total_host_holes, 0)
        self.assertEqual(reports[0].total_target_holes, 0)
        self.assertEqual(reports[0].total_face_holes, 0)
        self.assertEqual(reports[0].total_edge_holes, 0)
        self.assertFalse(reports[0].requires_review)

    def test_builder_uses_custom_family_mapping_injection(self):
        from domain.anchors import AnchorCoordinate, EdgeRef, HardwarePlacement, MountFace
        from manufacturing.hardware_intelligence_builder import (
            HardwareIntelligenceBuilder,
        )

        anchor = AnchorCoordinate(MountFace.LEFT, EdgeRef.FRONT, 0.0, 0.0)
        project = SimpleNamespace(
            placements=[
                HardwarePlacement("HOST_A", "INTENT_HANDLE", anchor, ""),
            ]
        )
        context = SimpleNamespace(
            hardware_profile={
                "INTENT_HANDLE": "HANDLE_128_BLACK",
            }
        )

        reports = HardwareIntelligenceBuilder(
            family_by_sku={"HANDLE_128_BLACK": "PULL"}
        ).build(project, context)

        self.assertEqual(len(reports), 1)
        self.assertEqual(reports[0].hardware_family, "PULL")
        self.assertEqual(reports[0].total_hardware_items, 1)
        self.assertEqual(reports[0].total_host_holes, 2)
        self.assertEqual(reports[0].total_target_holes, 0)
        self.assertEqual(reports[0].total_face_holes, 2)
        self.assertEqual(reports[0].total_edge_holes, 0)
        self.assertFalse(reports[0].requires_review)

    def test_builder_does_not_mutate_project_or_context(self):
        from domain.anchors import AnchorCoordinate, EdgeRef, HardwarePlacement, MountFace
        from manufacturing.hardware_intelligence_builder import (
            HardwareIntelligenceBuilder,
        )

        anchor = AnchorCoordinate(MountFace.LEFT, EdgeRef.FRONT, 0.0, 0.0)
        project = SimpleNamespace(
            placements=[
                HardwarePlacement("HOST_A", "INTENT_HINGE", anchor, "TARGET_A")
            ]
        )
        context = SimpleNamespace(
            hardware_profile={
                "INTENT_HINGE": "HINGE_BLUM_110_V1",
            }
        )

        placements_snapshot = [dict(placement.__dict__) for placement in project.placements]
        profile_snapshot = copy.deepcopy(context.hardware_profile)

        HardwareIntelligenceBuilder().build(project, context)

        self.assertEqual(
            [dict(placement.__dict__) for placement in project.placements],
            placements_snapshot,
        )
        self.assertEqual(context.hardware_profile, profile_snapshot)


if __name__ == "__main__":
    unittest.main()
