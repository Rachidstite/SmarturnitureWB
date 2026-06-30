from __future__ import annotations

from collections import defaultdict
from itertools import combinations
from typing import Iterable, Tuple

from domain.diagnostics import ConstraintViolation, Severity
from project_engineering.static_door_drawer_collision_decision import (
    StaticDoorDrawerCollisionDecision,
)
from project_engineering.static_door_drawer_collision_fact import (
    StaticDoorDrawerCollisionFact,
)
from project_engineering.static_door_drawer_collision_report import (
    StaticDoorDrawerCollisionReport,
)


class StaticDoorDrawerCollisionRule:
    COMPONENT_DOOR_PANEL = "DOOR_PANEL"
    COMPONENT_DRAWER_FACE = "DRAWER_FACE"
    DEFAULT_TOLERANCE_MM = 0.5
    WARNING_MULTIPLIER = 2.0

    @staticmethod
    def extract_facts(engineering_model) -> Tuple[StaticDoorDrawerCollisionFact, ...]:
        facts = []
        facts.extend(StaticDoorDrawerCollisionRule._extract_door_facts(engineering_model))
        facts.extend(
            StaticDoorDrawerCollisionRule._extract_drawer_face_facts(engineering_model)
        )
        facts.sort(
            key=lambda fact: (
                fact.section_id,
                fact.component_type,
                fact.component_id,
                fact.x_mm,
                fact.y_mm,
                fact.z_mm,
            )
        )
        return tuple(facts)

    @staticmethod
    def evaluate(
        engineering_model,
        tolerance_mm: float = DEFAULT_TOLERANCE_MM,
        source: str = "static-door-drawer-collision-rule",
    ) -> StaticDoorDrawerCollisionReport:
        facts = StaticDoorDrawerCollisionRule.extract_facts(engineering_model)
        grouped_facts = defaultdict(list)
        for fact in facts:
            if not fact.section_id:
                continue
            grouped_facts[fact.section_id].append(fact)

        violations = []
        checked_pair_count = 0
        warning_count = 0
        violation_count = 0

        for section_id, section_facts in grouped_facts.items():
            doors = [
                fact
                for fact in section_facts
                if fact.component_type == StaticDoorDrawerCollisionRule.COMPONENT_DOOR_PANEL
            ]
            drawer_faces = [
                fact
                for fact in section_facts
                if fact.component_type == StaticDoorDrawerCollisionRule.COMPONENT_DRAWER_FACE
            ]

            if not doors or not drawer_faces:
                continue

            for door, drawer_face in combinations(doors + drawer_faces, 2):
                if not StaticDoorDrawerCollisionRule._is_door_drawer_pair(door, drawer_face):
                    continue
                checked_pair_count += 1

                overlaps = StaticDoorDrawerCollisionRule._overlaps(door, drawer_face)
                if overlaps is None:
                    continue

                overlap_x, overlap_y, overlap_z = overlaps
                min_overlap = min(overlaps)
                is_warning = min_overlap <= tolerance_mm
                severity = Severity.WARNING if is_warning else Severity.ERROR
                status = "WARNING" if is_warning else "FAIL"
                code = (
                    "STATIC_DOOR_DRAWER_COLLISION_WARNING"
                    if is_warning
                    else "STATIC_DOOR_DRAWER_COLLISION_VIOLATION"
                )
                message = (
                    f"Static door-drawer collision in section {section_id}: "
                    f"{door.component_id} vs {drawer_face.component_id}; "
                    f"overlap_x={overlap_x:.3f}mm, "
                    f"overlap_y={overlap_y:.3f}mm, "
                    f"overlap_z={overlap_z:.3f}mm"
                )
                violations.append(
                    ConstraintViolation(
                        code=code,
                        message=message,
                        severity=severity,
                        node_id=f"{door.component_id} / {drawer_face.component_id}",
                        current_value=min_overlap,
                        required_value=tolerance_mm,
                        suggestion="Separate the door and drawer front within tolerance.",
                    )
                )
                if is_warning:
                    warning_count += 1
                else:
                    violation_count += 1

        if violation_count:
            status = "FAIL"
        elif warning_count:
            status = "WARNING"
        else:
            status = "PASS"

        decision = StaticDoorDrawerCollisionDecision(
            status=status,
            checked_pair_count=checked_pair_count,
            warning_count=warning_count,
            violation_count=violation_count,
            source=source,
        )

        return StaticDoorDrawerCollisionReport(
            facts=facts,
            decision=decision,
            violations=tuple(violations),
            tolerance_mm=tolerance_mm,
            source=source,
        )

    @staticmethod
    def _extract_door_facts(engineering_model) -> Iterable[StaticDoorDrawerCollisionFact]:
        for door in getattr(engineering_model, "doors", []) or []:
            yield StaticDoorDrawerCollisionFact(
                component_id=str(getattr(door, "name", "")),
                component_type=StaticDoorDrawerCollisionRule.COMPONENT_DOOR_PANEL,
                section_id=str(getattr(door, "section_id", "")),
                x_mm=float(getattr(door, "x_mm", 0.0)),
                y_mm=float(getattr(door, "y_mm", 0.0)),
                z_mm=float(getattr(door, "z_mm", 0.0)),
                width_mm=float(getattr(door, "width_mm", 0.0)),
                thickness_mm=float(getattr(door, "thickness_mm", 0.0)),
                height_mm=float(getattr(door, "height_mm", 0.0)),
                source=str(getattr(door, "source_rule", "")),
            )

    @staticmethod
    def _extract_drawer_face_facts(engineering_model) -> Iterable[StaticDoorDrawerCollisionFact]:
        for drawer_face in getattr(engineering_model, "drawer_faces", []) or []:
            yield StaticDoorDrawerCollisionFact(
                component_id=str(getattr(drawer_face, "name", "")),
                component_type=StaticDoorDrawerCollisionRule.COMPONENT_DRAWER_FACE,
                section_id=str(getattr(drawer_face, "section_id", "")),
                x_mm=float(getattr(drawer_face, "face_x_mm", 0.0)),
                y_mm=float(getattr(drawer_face, "face_y_mm", 0.0)),
                z_mm=float(getattr(drawer_face, "face_z_mm", 0.0)),
                width_mm=float(getattr(drawer_face, "face_w_mm", 0.0)),
                thickness_mm=float(getattr(drawer_face, "thickness_mm", 0.0)),
                height_mm=float(getattr(drawer_face, "face_h_mm", 0.0)),
                source=str(getattr(drawer_face, "source_rule", "")),
            )

    @staticmethod
    def _is_door_drawer_pair(
        left: StaticDoorDrawerCollisionFact,
        right: StaticDoorDrawerCollisionFact,
    ) -> bool:
        return {
            left.component_type,
            right.component_type,
        } == {
            StaticDoorDrawerCollisionRule.COMPONENT_DOOR_PANEL,
            StaticDoorDrawerCollisionRule.COMPONENT_DRAWER_FACE,
        }

    @staticmethod
    def _overlaps(
        left: StaticDoorDrawerCollisionFact,
        right: StaticDoorDrawerCollisionFact,
    ) -> tuple[float, float, float] | None:
        left_bounds = StaticDoorDrawerCollisionRule._bounds(left)
        right_bounds = StaticDoorDrawerCollisionRule._bounds(right)
        overlaps = []
        for axis in ("x", "y", "z"):
            overlap = min(left_bounds[axis][1], right_bounds[axis][1]) - max(
                left_bounds[axis][0], right_bounds[axis][0]
            )
            if overlap <= 0:
                return None
            overlaps.append(overlap)
        return overlaps[0], overlaps[1], overlaps[2]

    @staticmethod
    def _bounds(
        fact: StaticDoorDrawerCollisionFact,
    ) -> dict[str, tuple[float, float]]:
        return {
            "x": (fact.x_mm, fact.x_mm + fact.width_mm),
            "y": (fact.y_mm, fact.y_mm + fact.thickness_mm),
            "z": (fact.z_mm, fact.z_mm + fact.height_mm),
        }
