from __future__ import annotations

from typing import Iterable, Tuple

from domain.diagnostics import ConstraintViolation, Severity
from project_engineering.structural_consistency_decision import (
    StructuralConsistencyDecision,
)
from project_engineering.structural_consistency_fact import StructuralConsistencyFact
from project_engineering.structural_consistency_report import (
    StructuralConsistencyReport,
)


class StructuralConsistencyRule:
    COMPONENT_LEFT_SIDE_PANEL = "LEFT_SIDE_PANEL"
    COMPONENT_RIGHT_SIDE_PANEL = "RIGHT_SIDE_PANEL"
    COMPONENT_TOP_PANEL = "TOP_PANEL"
    COMPONENT_BOTTOM_PANEL = "BOTTOM_PANEL"
    COMPONENT_BACK_PANEL = "BACK_PANEL"
    COMPONENT_DOOR_PANEL = "DOOR_PANEL"
    COMPONENT_DRAWER_FACE = "DRAWER_FACE"
    COMPONENT_DRAWER_BOX = "DRAWER_BOX"
    COMPONENT_SHELF = "SHELF"
    COMPONENT_DIVIDER = "DIVIDER"

    STRUCTURAL_COMPONENT_TYPES = (
        COMPONENT_LEFT_SIDE_PANEL,
        COMPONENT_RIGHT_SIDE_PANEL,
        COMPONENT_TOP_PANEL,
        COMPONENT_BOTTOM_PANEL,
        COMPONENT_BACK_PANEL,
    )
    SECTION_SCOPED_COMPONENT_TYPES = (
        COMPONENT_DOOR_PANEL,
        COMPONENT_DRAWER_FACE,
        COMPONENT_DRAWER_BOX,
        COMPONENT_SHELF,
        COMPONENT_DIVIDER,
    )
    DEFAULT_TOLERANCE_MM = 0.5

    @staticmethod
    def extract_facts(engineering_model) -> Tuple[StructuralConsistencyFact, ...]:
        facts = []
        facts.extend(StructuralConsistencyRule._extract_carcass_facts(engineering_model))
        facts.extend(StructuralConsistencyRule._extract_door_facts(engineering_model))
        facts.extend(StructuralConsistencyRule._extract_drawer_face_facts(engineering_model))
        facts.extend(StructuralConsistencyRule._extract_drawer_box_facts(engineering_model))
        facts.extend(StructuralConsistencyRule._extract_shelf_facts(engineering_model))
        facts.extend(StructuralConsistencyRule._extract_divider_facts(engineering_model))
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
        source: str = "structural-consistency-rule",
    ) -> StructuralConsistencyReport:
        facts = StructuralConsistencyRule.extract_facts(engineering_model)
        violations = []
        warning_count = 0
        violation_count = 0
        checked_component_count = 0

        spec = getattr(getattr(engineering_model, "construction_model", None), "specification", None)
        if spec is None:
            violation_count += 1
            violations.append(
                ConstraintViolation(
                    code="STRUCTURAL_CONSISTENCY_MISSING_SPECIFICATION",
                    message="Engineering model has no construction specification.",
                    severity=Severity.ERROR,
                    node_id="cabinet",
                    suggestion="Provide a construction specification for structural checks.",
                )
            )
            decision = StructuralConsistencyDecision(
                status="FAIL",
                checked_component_count=0,
                warning_count=warning_count,
                violation_count=violation_count,
                source=source,
            )
            return StructuralConsistencyReport(
                facts=facts,
                decision=decision,
                violations=tuple(violations),
                source=source,
            )

        cabinet_width = float(getattr(spec, "width_mm", 0.0))
        cabinet_height = float(getattr(spec, "height_mm", 0.0))
        cabinet_depth = float(getattr(spec, "depth_mm", 0.0))
        side_thickness = StructuralConsistencyRule._positive_float(
            getattr(engineering_model.left_side_panel, "thickness_mm", 0.0)
            if getattr(engineering_model, "left_side_panel", None) is not None
            else getattr(spec, "material_thickness_mm", 0.0)
        )
        back_thickness = StructuralConsistencyRule._positive_float(
            getattr(engineering_model.back_panel, "thickness_mm", 0.0)
            if getattr(engineering_model, "back_panel", None) is not None
            else getattr(spec, "back_panel_thickness_mm", 0.0)
        )
        front_zone_depth = max(float(getattr(spec, "material_thickness_mm", 0.0)) * 2.0, 0.0)

        required_panels = [
            ("left_side_panel", StructuralConsistencyRule.COMPONENT_LEFT_SIDE_PANEL),
            ("right_side_panel", StructuralConsistencyRule.COMPONENT_RIGHT_SIDE_PANEL),
            ("top_panel", StructuralConsistencyRule.COMPONENT_TOP_PANEL),
            ("bottom_panel", StructuralConsistencyRule.COMPONENT_BOTTOM_PANEL),
        ]
        if str(getattr(spec, "back_panel_type", "") or "").upper() != "NONE":
            required_panels.append(
                ("back_panel", StructuralConsistencyRule.COMPONENT_BACK_PANEL)
            )
        for attribute_name, component_type in required_panels:
            checked_component_count += 1
            component = getattr(engineering_model, attribute_name, None)
            if component is None:
                violation_count += 1
                violations.append(
                    ConstraintViolation(
                        code="STRUCTURAL_CONSISTENCY_MISSING_CARCASS_COMPONENT",
                        message=f"Missing core carcass component: {attribute_name}.",
                        severity=Severity.ERROR,
                        node_id=attribute_name,
                        suggestion="Provide the full cabinet carcass before structural validation.",
                    )
                )
                continue

            dimension_violation = StructuralConsistencyRule._validate_positive_dimensions(
                component_type,
                attribute_name,
                StructuralConsistencyRule._panel_bounds(attribute_name, component, cabinet_width, cabinet_height, cabinet_depth),
                tolerance_mm,
            )
            if dimension_violation is not None:
                severity, message, current_value, required_value = dimension_violation
                if severity == Severity.WARNING:
                    warning_count += 1
                else:
                    violation_count += 1
                violations.append(
                    ConstraintViolation(
                        code=(
                            "STRUCTURAL_CONSISTENCY_WARNING"
                            if severity == Severity.WARNING
                            else "STRUCTURAL_CONSISTENCY_VIOLATION"
                        ),
                        message=message,
                        severity=severity,
                        node_id=attribute_name,
                        current_value=current_value,
                        required_value=required_value,
                        suggestion="Keep core carcass components fully inside the cabinet envelope.",
                    )
                )

        for fact in facts:
            if fact.component_type in StructuralConsistencyRule.STRUCTURAL_COMPONENT_TYPES:
                continue

            checked_component_count += 1

            if fact.component_type in StructuralConsistencyRule.SECTION_SCOPED_COMPONENT_TYPES and not fact.section_id:
                violation_count += 1
                violations.append(
                    ConstraintViolation(
                        code="STRUCTURAL_CONSISTENCY_SECTION_ID_MISSING",
                        message=(
                            f"Section-scoped component {fact.component_id} "
                            f"({fact.component_type}) has no section_id."
                        ),
                        severity=Severity.ERROR,
                        node_id=fact.component_id,
                        suggestion="Assign a section_id to all section-scoped engineering facts.",
                    )
                )
                continue

            if fact.component_type in (
                StructuralConsistencyRule.COMPONENT_SHELF,
                StructuralConsistencyRule.COMPONENT_DIVIDER,
                StructuralConsistencyRule.COMPONENT_DRAWER_BOX,
            ):
                bounds = StructuralConsistencyRule._component_bounds(fact)
                enclosure = (
                    (side_thickness, cabinet_width - side_thickness),
                    (0.0, cabinet_depth),
                    (0.0, cabinet_height),
                )
                result = StructuralConsistencyRule._evaluate_enclosure(
                    fact,
                    bounds,
                    enclosure,
                    tolerance_mm,
                    "inside cabinet bounds",
                )
                if result is not None:
                    severity, message, current_value, required_value = result
                    if severity == Severity.WARNING:
                        warning_count += 1
                    else:
                        violation_count += 1
                    violations.append(
                        ConstraintViolation(
                            code=(
                                "STRUCTURAL_CONSISTENCY_WARNING"
                                if severity == Severity.WARNING
                                else "STRUCTURAL_CONSISTENCY_VIOLATION"
                            ),
                            message=message,
                            severity=severity,
                            node_id=fact.component_id,
                            current_value=current_value,
                            required_value=required_value,
                            suggestion="Place the component fully inside the cabinet envelope.",
                        )
                    )
                continue

            if fact.component_type in (
                StructuralConsistencyRule.COMPONENT_DOOR_PANEL,
                StructuralConsistencyRule.COMPONENT_DRAWER_FACE,
            ):
                bounds = StructuralConsistencyRule._component_bounds(fact)
                enclosure = (
                    (side_thickness, cabinet_width - side_thickness),
                    (0.0, max(front_zone_depth, back_thickness)),
                    (0.0, cabinet_height),
                )
                result = StructuralConsistencyRule._evaluate_enclosure(
                    fact,
                    bounds,
                    enclosure,
                    tolerance_mm,
                    "inside front zone",
                )
                if result is not None:
                    severity, message, current_value, required_value = result
                    if severity == Severity.WARNING:
                        warning_count += 1
                    else:
                        violation_count += 1
                    violations.append(
                        ConstraintViolation(
                            code=(
                                "STRUCTURAL_CONSISTENCY_WARNING"
                                if severity == Severity.WARNING
                                else "STRUCTURAL_CONSISTENCY_VIOLATION"
                            ),
                            message=message,
                            severity=severity,
                            node_id=fact.component_id,
                            current_value=current_value,
                            required_value=required_value,
                            suggestion="Keep visible front components in the modeled front zone.",
                        )
                    )

        if violation_count:
            status = "FAIL"
        elif warning_count:
            status = "WARNING"
        else:
            status = "PASS"

        decision = StructuralConsistencyDecision(
            status=status,
            checked_component_count=checked_component_count,
            warning_count=warning_count,
            violation_count=violation_count,
            source=source,
        )

        return StructuralConsistencyReport(
            facts=facts,
            decision=decision,
            violations=tuple(violations),
            source=source,
        )

    @staticmethod
    def _extract_carcass_facts(engineering_model) -> Iterable[StructuralConsistencyFact]:
        panels = (
            (
                "left_side_panel",
                StructuralConsistencyRule.COMPONENT_LEFT_SIDE_PANEL,
            ),
            (
                "right_side_panel",
                StructuralConsistencyRule.COMPONENT_RIGHT_SIDE_PANEL,
            ),
            ("top_panel", StructuralConsistencyRule.COMPONENT_TOP_PANEL),
            ("bottom_panel", StructuralConsistencyRule.COMPONENT_BOTTOM_PANEL),
            ("back_panel", StructuralConsistencyRule.COMPONENT_BACK_PANEL),
        )
        for attribute_name, component_type in panels:
            panel = getattr(engineering_model, attribute_name, None)
            if panel is None:
                continue
            x_mm, y_mm, z_mm = StructuralConsistencyRule._position_tuple(
                getattr(panel, "position_mm", (0.0, 0.0, 0.0))
            )
            yield StructuralConsistencyFact(
                component_id=str(getattr(panel, "name", attribute_name)),
                component_type=component_type,
                section_id="",
                x_mm=x_mm,
                y_mm=y_mm,
                z_mm=z_mm,
                width_mm=float(getattr(panel, "width_mm", 0.0)),
                height_mm=float(getattr(panel, "height_mm", 0.0)),
                depth_mm=float(getattr(panel, "depth_mm", 0.0)),
                thickness_mm=float(getattr(panel, "thickness_mm", 0.0)),
                source=str(getattr(panel, "source_rule", "")),
            )

    @staticmethod
    def _extract_door_facts(engineering_model) -> Iterable[StructuralConsistencyFact]:
        for door in getattr(engineering_model, "doors", []) or []:
            yield StructuralConsistencyFact(
                component_id=str(getattr(door, "name", "")),
                component_type=StructuralConsistencyRule.COMPONENT_DOOR_PANEL,
                section_id=str(getattr(door, "section_id", "")),
                x_mm=float(getattr(door, "x_mm", 0.0)),
                y_mm=float(getattr(door, "y_mm", 0.0)),
                z_mm=float(getattr(door, "z_mm", 0.0)),
                width_mm=float(getattr(door, "width_mm", 0.0)),
                height_mm=float(getattr(door, "height_mm", 0.0)),
                depth_mm=float(getattr(door, "thickness_mm", 0.0)),
                thickness_mm=float(getattr(door, "thickness_mm", 0.0)),
                source=str(getattr(door, "source_rule", "")),
            )

    @staticmethod
    def _extract_drawer_face_facts(engineering_model) -> Iterable[StructuralConsistencyFact]:
        for drawer_face in getattr(engineering_model, "drawer_faces", []) or []:
            yield StructuralConsistencyFact(
                component_id=str(getattr(drawer_face, "name", "")),
                component_type=StructuralConsistencyRule.COMPONENT_DRAWER_FACE,
                section_id=str(getattr(drawer_face, "section_id", "")),
                x_mm=float(getattr(drawer_face, "face_x_mm", 0.0)),
                y_mm=float(getattr(drawer_face, "face_y_mm", 0.0)),
                z_mm=float(getattr(drawer_face, "face_z_mm", 0.0)),
                width_mm=float(getattr(drawer_face, "face_w_mm", 0.0)),
                height_mm=float(getattr(drawer_face, "face_h_mm", 0.0)),
                depth_mm=float(getattr(drawer_face, "thickness_mm", 0.0)),
                thickness_mm=float(getattr(drawer_face, "thickness_mm", 0.0)),
                source=str(getattr(drawer_face, "source_rule", "")),
            )

    @staticmethod
    def _extract_drawer_box_facts(engineering_model) -> Iterable[StructuralConsistencyFact]:
        for drawer_box in getattr(engineering_model, "drawer_boxes", []) or []:
            yield StructuralConsistencyFact(
                component_id=str(getattr(drawer_box, "name", "")),
                component_type=StructuralConsistencyRule.COMPONENT_DRAWER_BOX,
                section_id=str(getattr(drawer_box, "section_id", "")),
                x_mm=float(getattr(drawer_box, "box_x_mm", 0.0)),
                y_mm=float(getattr(drawer_box, "box_y_mm", 0.0)),
                z_mm=float(getattr(drawer_box, "box_z_mm", 0.0)),
                width_mm=float(getattr(drawer_box, "box_w_mm", 0.0)),
                height_mm=float(getattr(drawer_box, "box_h_mm", 0.0)),
                depth_mm=float(getattr(drawer_box, "box_d_mm", 0.0)),
                thickness_mm=float(getattr(drawer_box, "side_thickness_mm", 0.0)),
                source=str(getattr(drawer_box, "source_rule", "")),
            )

    @staticmethod
    def _extract_shelf_facts(engineering_model) -> Iterable[StructuralConsistencyFact]:
        for shelf in getattr(engineering_model, "shelves", []) or []:
            x_mm, y_mm, z_mm = StructuralConsistencyRule._position_tuple(
                getattr(shelf, "position_mm", (0.0, 0.0, 0.0))
            )
            yield StructuralConsistencyFact(
                component_id=str(getattr(shelf, "name", "")),
                component_type=StructuralConsistencyRule.COMPONENT_SHELF,
                section_id=str(getattr(shelf, "section_id", "")),
                x_mm=x_mm,
                y_mm=y_mm,
                z_mm=z_mm,
                width_mm=float(getattr(shelf, "width_mm", 0.0)),
                height_mm=float(getattr(shelf, "thickness_mm", 0.0)),
                depth_mm=float(getattr(shelf, "depth_mm", 0.0)),
                thickness_mm=float(getattr(shelf, "thickness_mm", 0.0)),
                source=str(getattr(shelf, "source_rule", "")),
            )

    @staticmethod
    def _extract_divider_facts(engineering_model) -> Iterable[StructuralConsistencyFact]:
        for divider in getattr(engineering_model, "dividers", []) or []:
            x_mm, y_mm, z_mm = StructuralConsistencyRule._position_tuple(
                getattr(divider, "position_mm", (0.0, 0.0, 0.0))
            )
            yield StructuralConsistencyFact(
                component_id=str(getattr(divider, "name", "")),
                component_type=StructuralConsistencyRule.COMPONENT_DIVIDER,
                section_id=str(getattr(divider, "section_id", "")),
                x_mm=x_mm,
                y_mm=y_mm,
                z_mm=z_mm,
                width_mm=float(getattr(divider, "width_mm", 0.0)),
                height_mm=float(getattr(divider, "height_mm", 0.0)),
                depth_mm=float(getattr(divider, "depth_mm", 0.0)),
                thickness_mm=float(getattr(divider, "width_mm", 0.0)),
                source=str(getattr(divider, "source_rule", "")),
            )

    @staticmethod
    def _panel_bounds(
        attribute_name: str,
        component,
        cabinet_width: float,
        cabinet_height: float,
        cabinet_depth: float,
    ) -> dict[str, tuple[float, float]]:
        x_mm, y_mm, z_mm = StructuralConsistencyRule._position_tuple(
            getattr(component, "position_mm", (0.0, 0.0, 0.0))
        )
        width_mm = float(getattr(component, "width_mm", 0.0))
        depth_mm = float(getattr(component, "depth_mm", 0.0))
        height_mm = float(getattr(component, "height_mm", 0.0))
        if attribute_name == "left_side_panel":
            return {
                "x": (x_mm, x_mm + width_mm),
                "y": (y_mm, y_mm + depth_mm),
                "z": (z_mm, z_mm + height_mm),
            }
        if attribute_name == "right_side_panel":
            return {
                "x": (x_mm, x_mm + width_mm),
                "y": (y_mm, y_mm + depth_mm),
                "z": (z_mm, z_mm + height_mm),
            }
        if attribute_name == "top_panel":
            return {
                "x": (x_mm, x_mm + width_mm),
                "y": (y_mm, y_mm + depth_mm),
                "z": (z_mm, z_mm + height_mm),
            }
        if attribute_name == "bottom_panel":
            return {
                "x": (x_mm, x_mm + width_mm),
                "y": (y_mm, y_mm + depth_mm),
                "z": (z_mm, z_mm + height_mm),
            }
        return {
            "x": (x_mm, x_mm + width_mm),
            "y": (y_mm, y_mm + depth_mm),
            "z": (z_mm, z_mm + height_mm),
        }

    @staticmethod
    def _component_bounds(fact: StructuralConsistencyFact) -> dict[str, tuple[float, float]]:
        return {
            "x": (fact.x_mm, fact.x_mm + fact.width_mm),
            "y": (fact.y_mm, fact.y_mm + (fact.depth_mm or fact.thickness_mm)),
            "z": (fact.z_mm, fact.z_mm + fact.height_mm),
        }

    @staticmethod
    def _evaluate_enclosure(
        fact: StructuralConsistencyFact,
        bounds: dict[str, tuple[float, float]],
        enclosure: tuple[tuple[float, float], tuple[float, float], tuple[float, float]],
        tolerance_mm: float,
        label: str,
    ) -> tuple[Severity, str, float, float] | None:
        axes = ("x", "y", "z")
        max_outside = 0.0
        min_clearance = None
        for axis, (low, high) in zip(axes, enclosure):
            comp_low, comp_high = bounds[axis]
            outside = max(low - comp_low, comp_high - high, 0.0)
            max_outside = max(max_outside, outside)
            clearance = min(comp_low - low, high - comp_high)
            min_clearance = clearance if min_clearance is None else min(min_clearance, clearance)

        if max_outside > tolerance_mm:
            return (
                Severity.ERROR,
                f"{fact.component_type} {fact.component_id} is outside {label}.",
                max_outside,
                tolerance_mm,
            )
        if max_outside > 0.0 or (min_clearance is not None and min_clearance <= tolerance_mm):
            return (
                Severity.WARNING,
                f"{fact.component_type} {fact.component_id} is tight against {label}.",
                max_outside if max_outside > 0.0 else float(min_clearance or 0.0),
                tolerance_mm,
            )
        return None

    @staticmethod
    def _validate_positive_dimensions(
        component_type: str,
        component_id: str,
        bounds: dict[str, tuple[float, float]],
        tolerance_mm: float,
    ) -> tuple[Severity, str, float, float] | None:
        for axis, (low, high) in bounds.items():
            if high <= low:
                return (
                    Severity.ERROR,
                    f"{component_type} {component_id} has invalid {axis}-axis dimensions.",
                    high - low,
                    tolerance_mm,
                )
        return None

    @staticmethod
    def _position_tuple(position) -> tuple[float, float, float]:
        values = tuple(position or (0.0, 0.0, 0.0))
        if len(values) != 3:
            return 0.0, 0.0, 0.0
        return float(values[0]), float(values[1]), float(values[2])

    @staticmethod
    def _positive_float(value: float) -> float:
        return float(value) if float(value) > 0.0 else 0.0
