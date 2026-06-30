from __future__ import annotations

from collections import defaultdict
from dataclasses import replace
from typing import Iterable, Tuple

from domain.diagnostics import ConstraintViolation, Severity
from project_engineering.reveal_validation_decision import RevealValidationDecision
from project_engineering.reveal_validation_fact import RevealValidationFact
from project_engineering.reveal_validation_report import RevealValidationReport


class RevealValidationRule:
    COMPONENT_DOOR_PANEL = "DOOR_PANEL"
    COMPONENT_DRAWER_FACE = "DRAWER_FACE"
    DEFAULT_TARGET_REVEAL_MM = 2.0
    DEFAULT_TOLERANCE_MM = 0.5

    @staticmethod
    def extract_facts(engineering_model) -> Tuple[RevealValidationFact, ...]:
        facts = []
        facts.extend(RevealValidationRule._extract_door_facts(engineering_model))
        facts.extend(RevealValidationRule._extract_drawer_face_facts(engineering_model))
        facts.sort(
            key=lambda fact: (
                fact.section_id,
                fact.component_type,
                fact.component_id,
                fact.x_mm,
                fact.z_mm,
            )
        )
        return tuple(facts)

    @staticmethod
    def evaluate(
        engineering_model,
        target_reveal_mm: float = DEFAULT_TARGET_REVEAL_MM,
        tolerance_mm: float = DEFAULT_TOLERANCE_MM,
        source: str = "reveal-validation-rule",
    ) -> RevealValidationReport:
        facts = RevealValidationRule.extract_facts(engineering_model)
        grouped_facts = defaultdict(list)
        for fact in facts:
            if not fact.section_id:
                continue
            grouped_facts[fact.section_id].append(fact)

        violations = []
        checked_gap_count = 0
        warning_count = 0
        violation_count = 0

        for section_id, section_facts in grouped_facts.items():
            checked_gap_count += RevealValidationRule._evaluate_horizontal_gaps(
                section_id,
                section_facts,
                target_reveal_mm,
                tolerance_mm,
                violations,
            )
            checked_gap_count += RevealValidationRule._evaluate_vertical_gaps(
                section_id,
                section_facts,
                target_reveal_mm,
                tolerance_mm,
                violations,
            )

        warning_count = sum(1 for violation in violations if violation.severity == Severity.WARNING)
        violation_count = sum(1 for violation in violations if violation.severity == Severity.ERROR)

        if violation_count:
            status = "FAIL"
        elif warning_count:
            status = "WARNING"
        else:
            status = "PASS"

        decision = RevealValidationDecision(
            status=status,
            checked_gap_count=checked_gap_count,
            warning_count=warning_count,
            violation_count=violation_count,
            source=source,
        )

        return RevealValidationReport(
            facts=facts,
            decision=decision,
            violations=tuple(violations),
            target_reveal_mm=target_reveal_mm,
            tolerance_mm=tolerance_mm,
            source=source,
        )

    @staticmethod
    def _extract_door_facts(engineering_model) -> Iterable[RevealValidationFact]:
        for door in getattr(engineering_model, "doors", []) or []:
            yield RevealValidationFact(
                component_id=str(getattr(door, "name", "")),
                component_type=RevealValidationRule.COMPONENT_DOOR_PANEL,
                section_id=str(getattr(door, "section_id", "")),
                x_mm=float(getattr(door, "x_mm", 0.0)),
                z_mm=float(getattr(door, "z_mm", 0.0)),
                width_mm=float(getattr(door, "width_mm", 0.0)),
                height_mm=float(getattr(door, "height_mm", 0.0)),
                source=str(getattr(door, "source_rule", "")),
            )

    @staticmethod
    def _extract_drawer_face_facts(engineering_model) -> Iterable[RevealValidationFact]:
        for drawer_face in getattr(engineering_model, "drawer_faces", []) or []:
            yield RevealValidationFact(
                component_id=str(getattr(drawer_face, "name", "")),
                component_type=RevealValidationRule.COMPONENT_DRAWER_FACE,
                section_id=str(getattr(drawer_face, "section_id", "")),
                x_mm=float(getattr(drawer_face, "face_x_mm", 0.0)),
                z_mm=float(getattr(drawer_face, "face_z_mm", 0.0)),
                width_mm=float(getattr(drawer_face, "face_w_mm", 0.0)),
                height_mm=float(getattr(drawer_face, "face_h_mm", 0.0)),
                source=str(getattr(drawer_face, "source_rule", "")),
            )

    @staticmethod
    def _evaluate_horizontal_gaps(
        section_id: str,
        section_facts: list[RevealValidationFact],
        target_reveal_mm: float,
        tolerance_mm: float,
        violations: list[ConstraintViolation],
    ) -> int:
        candidates = [
            fact
            for fact in section_facts
            if RevealValidationRule._z_overlap_width(fact, section_facts) > 0
        ]
        ordered = sorted(candidates, key=lambda fact: (fact.x_mm, fact.component_id))
        checked = 0
        for left, right in zip(ordered, ordered[1:]):
            if not RevealValidationRule._z_overlaps(left, right):
                continue
            gap = right.x_mm - (left.x_mm + left.width_mm)
            if gap < 0:
                continue
            checked += 1
            RevealValidationRule._append_violation(
                violations,
                section_id,
                left,
                right,
                "horizontal",
                gap,
                target_reveal_mm,
                tolerance_mm,
            )
        return checked

    @staticmethod
    def _evaluate_vertical_gaps(
        section_id: str,
        section_facts: list[RevealValidationFact],
        target_reveal_mm: float,
        tolerance_mm: float,
        violations: list[ConstraintViolation],
    ) -> int:
        candidates = [
            fact
            for fact in section_facts
            if RevealValidationRule._x_overlap_width(fact, section_facts) > 0
        ]
        ordered = sorted(candidates, key=lambda fact: (fact.z_mm, fact.component_id))
        checked = 0
        for lower, upper in zip(ordered, ordered[1:]):
            if not RevealValidationRule._x_overlaps(lower, upper):
                continue
            gap = upper.z_mm - (lower.z_mm + lower.height_mm)
            if gap < 0:
                continue
            checked += 1
            RevealValidationRule._append_violation(
                violations,
                section_id,
                lower,
                upper,
                "vertical",
                gap,
                target_reveal_mm,
                tolerance_mm,
            )
        return checked

    @staticmethod
    def _append_violation(
        violations: list[ConstraintViolation],
        section_id: str,
        first: RevealValidationFact,
        second: RevealValidationFact,
        orientation: str,
        gap_mm: float,
        target_reveal_mm: float,
        tolerance_mm: float,
    ) -> None:
        delta = abs(gap_mm - target_reveal_mm)
        if delta <= tolerance_mm:
            return
        severity = Severity.WARNING if delta <= (tolerance_mm * 2.0) else Severity.ERROR
        code = (
            "REVEAL_VALIDATION_WARNING"
            if severity == Severity.WARNING
            else "REVEAL_VALIDATION_VIOLATION"
        )
        violations.append(
            ConstraintViolation(
                code=code,
                message=(
                    f"Reveal deviation in section {section_id}: "
                    f"{first.component_id} vs {second.component_id} "
                    f"({orientation}); gap={gap_mm:.3f}mm, "
                    f"target={target_reveal_mm:.3f}mm"
                ),
                severity=severity,
                node_id=f"{first.component_id} / {second.component_id}",
                current_value=gap_mm,
                required_value=target_reveal_mm,
                suggestion="Adjust the visible front reveal toward the target.",
            )
        )

    @staticmethod
    def _x_overlap_width(
        fact: RevealValidationFact,
        facts: list[RevealValidationFact],
    ) -> float:
        other_x_min = min(other.x_mm for other in facts)
        other_x_max = max(other.x_mm + other.width_mm for other in facts)
        return min(fact.x_mm + fact.width_mm, other_x_max) - max(fact.x_mm, other_x_min)

    @staticmethod
    def _z_overlap_width(
        fact: RevealValidationFact,
        facts: list[RevealValidationFact],
    ) -> float:
        other_z_min = min(other.z_mm for other in facts)
        other_z_max = max(other.z_mm + other.height_mm for other in facts)
        return min(fact.z_mm + fact.height_mm, other_z_max) - max(fact.z_mm, other_z_min)

    @staticmethod
    def _x_overlaps(left: RevealValidationFact, right: RevealValidationFact) -> bool:
        return min(left.x_mm + left.width_mm, right.x_mm + right.width_mm) - max(
            left.x_mm, right.x_mm
        ) > 0

    @staticmethod
    def _z_overlaps(left: RevealValidationFact, right: RevealValidationFact) -> bool:
        return min(left.z_mm + left.height_mm, right.z_mm + right.height_mm) - max(
            left.z_mm, right.z_mm
        ) > 0
