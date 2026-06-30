from __future__ import annotations

from collections import defaultdict
from itertools import combinations
from typing import Iterable, Tuple

from domain.diagnostics import ConstraintViolation, Severity
from project_engineering.front_alignment_decision import FrontAlignmentDecision
from project_engineering.front_alignment_fact import FrontAlignmentFact
from project_engineering.front_alignment_report import FrontAlignmentReport


class FrontAlignmentRule:
    DEFAULT_TOLERANCE_MM = 0.5
    WARNING_MULTIPLIER = 2.0

    @staticmethod
    def extract_facts(engineering_model) -> Tuple[FrontAlignmentFact, ...]:
        facts = []
        facts.extend(FrontAlignmentRule._extract_door_facts(engineering_model))
        facts.extend(FrontAlignmentRule._extract_drawer_face_facts(engineering_model))
        facts.sort(
            key=lambda fact: (
                fact.section_id,
                fact.component_type,
                fact.component_index,
                fact.component_id,
            )
        )
        return tuple(facts)

    @staticmethod
    def evaluate(
        engineering_model,
        tolerance_mm: float = DEFAULT_TOLERANCE_MM,
        source: str = "front-alignment-rule",
    ) -> FrontAlignmentReport:
        facts = FrontAlignmentRule.extract_facts(engineering_model)
        grouped_facts = defaultdict(list)
        for fact in facts:
            grouped_facts[FrontAlignmentRule._section_key(fact.section_id)].append(fact)

        violations = []
        component_statuses = {fact.component_id: "PASS" for fact in facts}

        for section_id, section_facts in grouped_facts.items():
            if len(section_facts) < 2:
                continue
            for left, right in combinations(section_facts, 2):
                deltas = FrontAlignmentRule._edge_deltas(left, right)
                max_delta = max(abs(delta) for delta in deltas.values())
                if max_delta <= tolerance_mm:
                    continue

                is_warning = max_delta <= (tolerance_mm * FrontAlignmentRule.WARNING_MULTIPLIER)
                severity = Severity.WARNING if is_warning else Severity.ERROR
                status = "WARNING" if is_warning else "FAIL"
                code = (
                    "FRONT_ALIGNMENT_WARNING"
                    if is_warning
                    else "FRONT_ALIGNMENT_VIOLATION"
                )
                message = (
                    f"Front alignment mismatch in section {section_id}: "
                    f"{left.component_id} vs {right.component_id}; "
                    f"left={deltas['left']:.3f}mm, "
                    f"right={deltas['right']:.3f}mm, "
                    f"top={deltas['top']:.3f}mm, "
                    f"bottom={deltas['bottom']:.3f}mm, "
                    f"front_plane={deltas['front_plane']:.3f}mm"
                )
                violations.append(
                    ConstraintViolation(
                        code=code,
                        message=message,
                        severity=severity,
                        node_id=f"{left.component_id} / {right.component_id}",
                        current_value=max_delta,
                        required_value=tolerance_mm,
                        suggestion="Align projected front edges within tolerance.",
                    )
                )
                FrontAlignmentRule._raise_status(component_statuses, left.component_id, status)
                FrontAlignmentRule._raise_status(component_statuses, right.component_id, status)

        aligned_component_count = sum(1 for status in component_statuses.values() if status == "PASS")
        warning_count = sum(1 for status in component_statuses.values() if status == "WARNING")
        violation_count = sum(1 for status in component_statuses.values() if status == "FAIL")

        if violation_count:
            status = "FAIL"
        elif warning_count:
            status = "WARNING"
        else:
            status = "PASS"

        decision = FrontAlignmentDecision(
            status=status,
            aligned_component_count=aligned_component_count,
            warning_count=warning_count,
            violation_count=violation_count,
            source=source,
        )

        return FrontAlignmentReport(
            facts=facts,
            decision=decision,
            violations=tuple(violations),
            tolerance_mm=tolerance_mm,
            source=source,
        )

    @staticmethod
    def _extract_door_facts(engineering_model) -> Iterable[FrontAlignmentFact]:
        for door in getattr(engineering_model, "doors", []) or []:
            yield FrontAlignmentFact(
                component_id=str(getattr(door, "name", "")),
                component_type="DOOR_PANEL",
                section_id=str(getattr(door, "section_id", "")),
                component_index=int(getattr(door, "door_index", 0)),
                x_mm=float(getattr(door, "x_mm", 0.0)),
                y_mm=float(getattr(door, "y_mm", 0.0)),
                z_mm=float(getattr(door, "z_mm", 0.0)),
                width_mm=float(getattr(door, "width_mm", 0.0)),
                height_mm=float(getattr(door, "height_mm", 0.0)),
                front_plane_mm=float(getattr(door, "y_mm", 0.0)),
                source=str(getattr(door, "source_rule", "")),
            )

    @staticmethod
    def _extract_drawer_face_facts(engineering_model) -> Iterable[FrontAlignmentFact]:
        for drawer_face in getattr(engineering_model, "drawer_faces", []) or []:
            yield FrontAlignmentFact(
                component_id=str(getattr(drawer_face, "name", "")),
                component_type="DRAWER_FACE",
                section_id=str(getattr(drawer_face, "section_id", "")),
                component_index=int(getattr(drawer_face, "drawer_index", 0)),
                x_mm=float(getattr(drawer_face, "face_x_mm", 0.0)),
                y_mm=float(getattr(drawer_face, "face_y_mm", 0.0)),
                z_mm=float(getattr(drawer_face, "face_z_mm", 0.0)),
                width_mm=float(getattr(drawer_face, "face_w_mm", 0.0)),
                height_mm=float(getattr(drawer_face, "face_h_mm", 0.0)),
                front_plane_mm=float(getattr(drawer_face, "face_y_mm", 0.0)),
                source=str(getattr(drawer_face, "source_rule", "")),
            )

    @staticmethod
    def _edge_deltas(left: FrontAlignmentFact, right: FrontAlignmentFact) -> dict[str, float]:
        left_edges = FrontAlignmentRule._edges(left)
        right_edges = FrontAlignmentRule._edges(right)
        return {
            edge: left_edges[edge] - right_edges[edge]
            for edge in ("left", "right", "top", "bottom", "front_plane")
        }

    @staticmethod
    def _edges(fact: FrontAlignmentFact) -> dict[str, float]:
        return {
            "left": fact.x_mm,
            "right": fact.x_mm + fact.width_mm,
            "top": fact.z_mm + fact.height_mm,
            "bottom": fact.z_mm,
            "front_plane": fact.front_plane_mm,
        }

    @staticmethod
    def _section_key(section_id: str) -> str:
        return section_id or "__GLOBAL__"

    @staticmethod
    def _raise_status(statuses: dict[str, str], component_id: str, new_status: str) -> None:
        current = statuses.get(component_id, "PASS")
        rank = {"PASS": 0, "WARNING": 1, "FAIL": 2}
        if rank[new_status] > rank[current]:
            statuses[component_id] = new_status
