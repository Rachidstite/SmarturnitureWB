from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict

from assembly.joint_rules import RULES
from assembly.assembly_graph_builder import AssemblyGraphBuilder


@dataclass
class HardwareReport:
    minifix_count: int = 0
    dowel_count: int = 0
    hinge_count: int = 0

    hardware_items: Dict[str, int] = field(default_factory=dict)

    hardware_cost: float = 0.0


class HardwareReportEngine:

    @staticmethod
    def generate(scene_graph):

        report = HardwareReport()

        assembly = AssemblyGraphBuilder.build(
            scene_graph
        )

        rules_by_type = {
            r.joint_type: r
            for r in RULES
        }

        for joint in assembly.all_joints():

            if joint.joint_type == "HINGE":
                report.hinge_count += 4
                continue

            rule = rules_by_type.get(
                joint.joint_type
            )

            if not rule:
                continue

            report.minifix_count += rule.minifix_count
            report.dowel_count += rule.dowel_count

        report.hardware_items["MINIFIX"] = report.minifix_count
        report.hardware_items["DOWEL"] = report.dowel_count
        report.hardware_items["HINGE"] = report.hinge_count

        return report

    @staticmethod
    def generate_from_project(project, context):
        report = HardwareReport()
        placements = getattr(project, "placements", []) or []
        hardware_profile = getattr(context, "hardware_profile", {}) or {}

        family_by_sku = {
            "HINGE_BLUM_110_V1": "HINGE",
            "MINIFIX_15_V1": "MINIFIX",
            "CONFIRMAT_50_V1": "CONFIRMAT",
            "SHELF_PIN_5MM": "SHELF_PIN",
            "DRAWER_SLIDE_SOFTCLOSE_450": "DRAWER_SLIDE",
            "DRAWER_SLIDE_STANDARD_450": "DRAWER_SLIDE",
        }

        counts = defaultdict(int)

        for placement in placements:
            intent = getattr(placement, "hardware_intent", None)
            if not intent:
                continue

            sku = hardware_profile.get(intent)
            if not sku:
                continue

            family = family_by_sku.get(sku)
            if not family:
                continue

            counts[family] += 1

        report.hinge_count = counts.get("HINGE", 0)
        report.minifix_count = counts.get("MINIFIX", 0)
        report.dowel_count = counts.get("DOWEL", 0)
        report.hardware_items["HINGE"] = report.hinge_count
        report.hardware_items["MINIFIX"] = report.minifix_count
        report.hardware_items["CONFIRMAT"] = counts.get("CONFIRMAT", 0)
        report.hardware_items["SHELF_PIN"] = counts.get("SHELF_PIN", 0)
        report.hardware_items["DRAWER_SLIDE"] = counts.get("DRAWER_SLIDE", 0)
        report.hardware_items["DOWEL"] = report.dowel_count

        return report
