from dataclasses import dataclass, field
from typing import Dict

from assembly.joint_rules import RULES
from assembly.assembly_graph_builder import AssemblyGraphBuilder
from domain.hardware_library import HardwareRegistry


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

        registry = HardwareRegistry()

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

        minifix = registry.get_hardware(
            "MINIFIX_15_V1"
        )

        hinge = registry.get_hardware(
            "HINGE_BLUM_110_V1"
        )

        if minifix:
            report.hardware_cost += (
                report.minifix_count *
                minifix.price
            )

        if hinge:
            report.hardware_cost += (
                report.hinge_count *
                hinge.price
            )

        return report
