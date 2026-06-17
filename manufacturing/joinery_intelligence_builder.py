from manufacturing.joinery_intelligence_report import (
    JoineryIntelligenceReport,
)


class JoineryIntelligenceBuilder:

    def build(self, project):
        placements = list(getattr(project, "placements", []) or [])
        nodes = list(getattr(project.graph, "physical_nodes", []) or [])

        total_minifix = self._count_intent(placements, "INTENT_MINIFIX")
        total_hinges = self._count_intent(placements, "INTENT_HINGE")
        total_drawer_slides = self._count_intent(
            placements, "INTENT_DRAWER_SLIDE"
        )
        total_handles = self._count_intent(placements, "INTENT_HANDLE")

        all_ops = []
        for node in nodes:
            all_ops.extend(list(getattr(node, "machining_ops", []) or []))

        total_face_holes = sum(
            1 for op in all_ops if self._is_face_hole(op)
        )
        total_edge_holes = sum(
            1 for op in all_ops if self._is_edge_hole(op)
        )
        total_cam_holes = sum(
            1 for op in all_ops if float(getattr(op, "diameter", 0.0)) == 15.0
        )

        joinery_complexity_score = (
            total_minifix
            + total_hinges
            + total_drawer_slides
            + total_handles
            + total_face_holes
            + total_edge_holes
        )

        warnings = []
        if total_minifix == 0 and total_hinges == 0:
            warnings.append("No primary joinery detected")

        return JoineryIntelligenceReport(
            total_minifix=total_minifix,
            total_hinges=total_hinges,
            total_drawer_slides=total_drawer_slides,
            total_handles=total_handles,
            total_face_holes=total_face_holes,
            total_edge_holes=total_edge_holes,
            total_cam_holes=total_cam_holes,
            joinery_complexity_score=joinery_complexity_score,
            warnings=warnings,
        )

    @staticmethod
    def _count_intent(placements, prefix):
        return sum(
            1
            for placement in placements
            if str(getattr(placement, "hardware_intent", "")).startswith(prefix)
        )

    @staticmethod
    def _is_edge_hole(operation):
        return str(getattr(operation, "axis", "Z")).upper() in {"X", "Y"}

    @staticmethod
    def _is_face_hole(operation):
        return not JoineryIntelligenceBuilder._is_edge_hole(operation)
