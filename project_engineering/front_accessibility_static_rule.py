from __future__ import annotations

from collections import defaultdict
from itertools import combinations
from typing import Iterable, Tuple

from domain.diagnostics import ConstraintViolation, Severity
from project_engineering.front_accessibility_static_decision import (
    FrontAccessibilityStaticDecision,
)
from project_engineering.front_accessibility_static_fact import (
    FrontAccessibilityStaticFact,
)
from project_engineering.front_accessibility_static_report import (
    FrontAccessibilityStaticReport,
)


class FrontAccessibilityStaticRule:
    COMPONENT_DOOR_PANEL = "DOOR_PANEL"
    COMPONENT_DRAWER_FACE = "DRAWER_FACE"
    COMPONENT_DRAWER_BOX = "DRAWER_BOX"
    COMPONENT_SHELF = "SHELF"
    COMPONENT_DIVIDER = "DIVIDER"
    COMPONENT_SIDE_PANEL = "SIDE_PANEL"

    ACCESS_TARGET_COMPONENT_TYPES = (
        COMPONENT_DOOR_PANEL,
        COMPONENT_DRAWER_FACE,
        COMPONENT_DRAWER_BOX,
    )
    STATIC_BLOCKER_COMPONENT_TYPES = (
        COMPONENT_SHELF,
        COMPONENT_DIVIDER,
    )
    DEFAULT_TOLERANCE_MM = 0.5
    WARNING_MULTIPLIER = 2.0

    @staticmethod
    def extract_facts(engineering_model) -> Tuple[FrontAccessibilityStaticFact, ...]:
        facts = []
        facts.extend(
            FrontAccessibilityStaticRule._extract_door_facts(engineering_model)
        )
        facts.extend(
            FrontAccessibilityStaticRule._extract_drawer_face_facts(engineering_model)
        )
        facts.extend(
            FrontAccessibilityStaticRule._extract_drawer_box_facts(engineering_model)
        )
        facts.extend(
            FrontAccessibilityStaticRule._extract_shelf_facts(engineering_model)
        )
        facts.extend(
            FrontAccessibilityStaticRule._extract_divider_facts(engineering_model)
        )
        facts.extend(
            FrontAccessibilityStaticRule._extract_side_panel_facts(engineering_model)
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
        source: str = "front-accessibility-static-rule",
    ) -> FrontAccessibilityStaticReport:
        facts = FrontAccessibilityStaticRule.extract_facts(engineering_model)
        grouped_facts = defaultdict(list)
        for fact in facts:
            if not fact.section_id:
                continue
            grouped_facts[fact.section_id].append(fact)

        violations = []
        checked_component_count = 0
        warning_count = 0
        violation_count = 0

        for section_id, section_facts in grouped_facts.items():
            access_targets = [
                fact
                for fact in section_facts
                if fact.component_type in FrontAccessibilityStaticRule.ACCESS_TARGET_COMPONENT_TYPES
            ]
            blockers = [
                fact
                for fact in section_facts
                if fact.component_type in FrontAccessibilityStaticRule.STATIC_BLOCKER_COMPONENT_TYPES
            ]
            checked_component_count += len(section_facts)

            if not access_targets or not blockers:
                continue

            for target, blocker in combinations(access_targets + blockers, 2):
                if not FrontAccessibilityStaticRule._is_target_blocker_pair(target, blocker):
                    continue

                overlap = FrontAccessibilityStaticRule._overlap(target, blocker)
                if overlap is None:
                    continue

                overlap_x, overlap_y, overlap_z = overlap
                min_overlap = min(overlap)
                is_warning = min_overlap <= tolerance_mm
                severity = Severity.WARNING if is_warning else Severity.ERROR
                code = (
                    "FRONT_ACCESSIBILITY_STATIC_WARNING"
                    if is_warning
                    else "FRONT_ACCESSIBILITY_STATIC_VIOLATION"
                )
                message = (
                    f"Front accessibility blocker in section {section_id}: "
                    f"{blocker.component_type} {blocker.component_id} blocks "
                    f"{target.component_type} {target.component_id}; "
                    f"overlap_x={overlap_x:.3f}mm, "
                    f"overlap_y={overlap_y:.3f}mm, "
                    f"overlap_z={overlap_z:.3f}mm"
                )
                violations.append(
                    ConstraintViolation(
                        code=code,
                        message=message,
                        severity=severity,
                        node_id=f"{target.component_id} / {blocker.component_id}",
                        current_value=min_overlap,
                        required_value=tolerance_mm,
                        suggestion="Clear the front access zone within the section.",
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

        decision = FrontAccessibilityStaticDecision(
            status=status,
            checked_component_count=checked_component_count,
            warning_count=warning_count,
            violation_count=violation_count,
            source=source,
        )

        return FrontAccessibilityStaticReport(
            facts=facts,
            decision=decision,
            violations=tuple(violations),
            tolerance_mm=tolerance_mm,
            source=source,
        )

    @staticmethod
    def _extract_door_facts(engineering_model) -> Iterable[FrontAccessibilityStaticFact]:
        for door in getattr(engineering_model, "doors", []) or []:
            yield FrontAccessibilityStaticFact(
                component_id=str(getattr(door, "name", "")),
                component_type=FrontAccessibilityStaticRule.COMPONENT_DOOR_PANEL,
                section_id=str(getattr(door, "section_id", "")),
                x_mm=float(getattr(door, "x_mm", 0.0)),
                y_mm=float(getattr(door, "y_mm", 0.0)),
                z_mm=float(getattr(door, "z_mm", 0.0)),
                width_mm=float(getattr(door, "width_mm", 0.0)),
                height_mm=float(getattr(door, "height_mm", 0.0)),
                depth_or_thickness_mm=float(getattr(door, "thickness_mm", 0.0)),
                source=str(getattr(door, "source_rule", "")),
            )

    @staticmethod
    def _extract_drawer_face_facts(engineering_model) -> Iterable[FrontAccessibilityStaticFact]:
        for drawer_face in getattr(engineering_model, "drawer_faces", []) or []:
            yield FrontAccessibilityStaticFact(
                component_id=str(getattr(drawer_face, "name", "")),
                component_type=FrontAccessibilityStaticRule.COMPONENT_DRAWER_FACE,
                section_id=str(getattr(drawer_face, "section_id", "")),
                x_mm=float(getattr(drawer_face, "face_x_mm", 0.0)),
                y_mm=float(getattr(drawer_face, "face_y_mm", 0.0)),
                z_mm=float(getattr(drawer_face, "face_z_mm", 0.0)),
                width_mm=float(getattr(drawer_face, "face_w_mm", 0.0)),
                height_mm=float(getattr(drawer_face, "face_h_mm", 0.0)),
                depth_or_thickness_mm=float(getattr(drawer_face, "thickness_mm", 0.0)),
                source=str(getattr(drawer_face, "source_rule", "")),
            )

    @staticmethod
    def _extract_drawer_box_facts(engineering_model) -> Iterable[FrontAccessibilityStaticFact]:
        for drawer_box in getattr(engineering_model, "drawer_boxes", []) or []:
            yield FrontAccessibilityStaticFact(
                component_id=str(getattr(drawer_box, "name", "")),
                component_type=FrontAccessibilityStaticRule.COMPONENT_DRAWER_BOX,
                section_id=str(getattr(drawer_box, "section_id", "")),
                x_mm=float(getattr(drawer_box, "box_x_mm", 0.0)),
                y_mm=float(getattr(drawer_box, "box_y_mm", 0.0)),
                z_mm=float(getattr(drawer_box, "box_z_mm", 0.0)),
                width_mm=float(getattr(drawer_box, "box_w_mm", 0.0)),
                height_mm=float(getattr(drawer_box, "box_h_mm", 0.0)),
                depth_or_thickness_mm=float(getattr(drawer_box, "box_d_mm", 0.0)),
                source=str(getattr(drawer_box, "source_rule", "")),
            )

    @staticmethod
    def _extract_shelf_facts(engineering_model) -> Iterable[FrontAccessibilityStaticFact]:
        for shelf in getattr(engineering_model, "shelves", []) or []:
            x_mm, y_mm, z_mm = FrontAccessibilityStaticRule._position_tuple(
                getattr(shelf, "position_mm", (0.0, 0.0, 0.0))
            )
            yield FrontAccessibilityStaticFact(
                component_id=str(getattr(shelf, "name", "")),
                component_type=FrontAccessibilityStaticRule.COMPONENT_SHELF,
                section_id=str(getattr(shelf, "section_id", "")),
                x_mm=x_mm,
                y_mm=y_mm,
                z_mm=z_mm,
                width_mm=float(getattr(shelf, "width_mm", 0.0)),
                height_mm=float(getattr(shelf, "thickness_mm", 0.0)),
                depth_or_thickness_mm=float(getattr(shelf, "depth_mm", 0.0)),
                source=str(getattr(shelf, "source_rule", "")),
            )

    @staticmethod
    def _extract_divider_facts(engineering_model) -> Iterable[FrontAccessibilityStaticFact]:
        for divider in getattr(engineering_model, "dividers", []) or []:
            x_mm, y_mm, z_mm = FrontAccessibilityStaticRule._position_tuple(
                getattr(divider, "position_mm", (0.0, 0.0, 0.0))
            )
            yield FrontAccessibilityStaticFact(
                component_id=str(getattr(divider, "name", "")),
                component_type=FrontAccessibilityStaticRule.COMPONENT_DIVIDER,
                section_id=str(getattr(divider, "section_id", "")),
                x_mm=x_mm,
                y_mm=y_mm,
                z_mm=z_mm,
                width_mm=float(getattr(divider, "width_mm", 0.0)),
                height_mm=float(getattr(divider, "height_mm", 0.0)),
                depth_or_thickness_mm=float(getattr(divider, "depth_mm", 0.0)),
                source=str(getattr(divider, "source_rule", "")),
            )

    @staticmethod
    def _extract_side_panel_facts(engineering_model) -> Iterable[FrontAccessibilityStaticFact]:
        for panel_name in ("left_side_panel", "right_side_panel"):
            panel = getattr(engineering_model, panel_name, None)
            if panel is None:
                continue
            x_mm, y_mm, z_mm = FrontAccessibilityStaticRule._position_tuple(
                getattr(panel, "position_mm", (0.0, 0.0, 0.0))
            )
            yield FrontAccessibilityStaticFact(
                component_id=str(getattr(panel, "name", panel_name)),
                component_type=FrontAccessibilityStaticRule.COMPONENT_SIDE_PANEL,
                section_id="",
                x_mm=x_mm,
                y_mm=y_mm,
                z_mm=z_mm,
                width_mm=float(getattr(panel, "width_mm", 0.0)),
                height_mm=float(getattr(panel, "height_mm", 0.0)),
                depth_or_thickness_mm=float(getattr(panel, "depth_mm", 0.0)),
                source=str(getattr(panel, "source_rule", "")),
            )

    @staticmethod
    def _is_target_blocker_pair(
        left: FrontAccessibilityStaticFact,
        right: FrontAccessibilityStaticFact,
    ) -> bool:
        return (
            left.component_type in FrontAccessibilityStaticRule.ACCESS_TARGET_COMPONENT_TYPES
            and right.component_type in FrontAccessibilityStaticRule.STATIC_BLOCKER_COMPONENT_TYPES
        ) or (
            right.component_type in FrontAccessibilityStaticRule.ACCESS_TARGET_COMPONENT_TYPES
            and left.component_type in FrontAccessibilityStaticRule.STATIC_BLOCKER_COMPONENT_TYPES
        )

    @staticmethod
    def _overlap(
        left: FrontAccessibilityStaticFact,
        right: FrontAccessibilityStaticFact,
    ) -> tuple[float, float, float] | None:
        left_bounds = FrontAccessibilityStaticRule._bounds(left)
        right_bounds = FrontAccessibilityStaticRule._bounds(right)
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
        fact: FrontAccessibilityStaticFact,
    ) -> dict[str, tuple[float, float]]:
        return {
            "x": (fact.x_mm, fact.x_mm + fact.width_mm),
            "y": (fact.y_mm, fact.y_mm + fact.depth_or_thickness_mm),
            "z": (fact.z_mm, fact.z_mm + fact.height_mm),
        }

    @staticmethod
    def _position_tuple(position) -> tuple[float, float, float]:
        if isinstance(position, tuple) and len(position) == 3:
            return float(position[0]), float(position[1]), float(position[2])
        return 0.0, 0.0, 0.0
