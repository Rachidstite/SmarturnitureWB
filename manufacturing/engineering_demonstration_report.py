from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from domain.core_types import NodeCategory, NodeRole


@dataclass(frozen=True)
class EngineeringDemonstrationReport:
    project_name: str = ""
    overall_width_mm: float = 0.0
    overall_height_mm: float = 0.0
    overall_depth_mm: float = 0.0
    material_thickness_mm: float = 0.0

    panel_count: int = 0
    hardware_count: int = 0
    drilling_count: int = 0

    role_counts: dict = field(default_factory=dict)
    hardware_intent_counts: dict = field(default_factory=dict)

    validation_status: str = "UNKNOWN"
    warnings: list = field(default_factory=list)

    estimated_manufacturing_cost: float | None = None
    currency: str = ""

    real_detail_lines: list = field(default_factory=list)
    prototype_detail_lines: list = field(default_factory=list)

    def to_lines(self) -> list[str]:
        lines = [
            "Visible Engineering Demonstration",
            (
                "Overall size: "
                f"{self.overall_width_mm:.0f} x {self.overall_height_mm:.0f} x "
                f"{self.overall_depth_mm:.0f} mm"
            ),
            f"Material thickness: {self.material_thickness_mm:.0f} mm",
            f"Panel count: {self.panel_count}",
            f"Hardware count: {self.hardware_count}",
            f"Drilling count: {self.drilling_count}",
            f"Validation status: {self.validation_status}",
        ]

        if self.estimated_manufacturing_cost is not None:
            currency = self.currency or ""
            lines.append(
                "Estimated manufacturing cost: "
                f"{self.estimated_manufacturing_cost:.2f} {currency}".strip()
            )
        else:
            lines.append("Estimated manufacturing cost: not available")

        if self.real_detail_lines:
            lines.append("Production-backed geometry:")
            lines.extend(self.real_detail_lines)

        if self.prototype_detail_lines:
            lines.append("Prototype-only geometry:")
            lines.extend(self.prototype_detail_lines)

        if self.warnings:
            lines.append("Warnings:")
            lines.extend(f"- {warning}" for warning in self.warnings)

        return lines


def build_engineering_demonstration_report(
    project,
    *,
    validation_state: Any = None,
    cost_summary: Any = None,
) -> EngineeringDemonstrationReport:
    graph = getattr(project, "graph", None)
    nodes = list(getattr(graph, "all_nodes", lambda: [])() or [])
    physical_nodes = [
        node for node in nodes if _is_physical_node(node)
    ]

    role_counts = _count_by_role(physical_nodes)
    hardware_intent_counts = _count_hardware_intents(
        list(getattr(project, "placements", []) or [])
    )
    drilling_count = sum(
        len(getattr(node, "machining_ops", []) or [])
        for node in physical_nodes
    )
    overall_width_mm, overall_height_mm, overall_depth_mm = _bounding_box(
        physical_nodes
    )
    material_thickness_mm = _first_thickness(physical_nodes)

    warnings = _collect_warnings(validation_state, cost_summary)
    validation_status = _validation_status(validation_state)
    estimated_manufacturing_cost, currency = _cost_summary(cost_summary)

    real_detail_lines = [
        f"Side panels: {role_counts.get('SIDE_PANEL', 0)}",
        f"Top panels: {role_counts.get('TOP_PANEL', 0)}",
        f"Bottom panels: {role_counts.get('BOTTOM_PANEL', 0)}",
        f"Shelves: {role_counts.get('SHELF', 0)}",
        f"Back panels: {role_counts.get('BACK_PANEL', 0)}",
        f"Doors: {role_counts.get('DOOR_PANEL', 0)}",
        f"Dividers: {role_counts.get('DIVIDER', 0)}",
        f"Hinge placements: {hardware_intent_counts.get('INTENT_HINGE', 0)}",
        f"Minifix placements: {hardware_intent_counts.get('INTENT_MINIFIX_15', 0)}",
        f"Confirmat placements: {hardware_intent_counts.get('INTENT_CONFIRMAT_50', 0)}",
        f"Shelf pin placements: {hardware_intent_counts.get('INTENT_SHELF_PIN', 0)}",
        f"Drawer slide placements: {hardware_intent_counts.get('INTENT_DRAWER_SLIDE', 0)}",
        f"Handle placements: {hardware_intent_counts.get('INTENT_HANDLE', 0)}",
    ]

    prototype_detail_lines = []
    if _has_wall_mount_data(project):
        prototype_detail_lines.append("Real wall mount data available")
    elif role_counts.get("BACK_PANEL", 0) > 0:
        prototype_detail_lines.append(
            "Wall mount geometry shown as a labeled engineering prototype"
        )

    return EngineeringDemonstrationReport(
        project_name=str(getattr(project, "uid", "") or ""),
        overall_width_mm=overall_width_mm,
        overall_height_mm=overall_height_mm,
        overall_depth_mm=overall_depth_mm,
        material_thickness_mm=material_thickness_mm,
        panel_count=len(physical_nodes),
        hardware_count=len(list(getattr(project, "placements", []) or [])),
        drilling_count=drilling_count,
        role_counts=role_counts,
        hardware_intent_counts=hardware_intent_counts,
        validation_status=validation_status,
        warnings=warnings,
        estimated_manufacturing_cost=estimated_manufacturing_cost,
        currency=currency,
        real_detail_lines=real_detail_lines,
        prototype_detail_lines=prototype_detail_lines,
    )


def _is_physical_node(node) -> bool:
    category = getattr(node, "category", None)
    if category is None:
        return True

    category_value = getattr(category, "value", category)
    return category_value == getattr(NodeCategory.PHYSICAL, "value", "PHYSICAL")


def _count_by_role(nodes) -> dict:
    counts = {}
    for node in nodes:
        role = getattr(node, "role", NodeRole.UNKNOWN)
        role_value = getattr(role, "value", role)
        role_key = str(role_value)
        counts[role_key] = counts.get(role_key, 0) + 1
    return counts


def _count_hardware_intents(placements) -> dict:
    counts = {}
    for placement in placements:
        intent = str(getattr(placement, "hardware_intent", "") or "")
        if not intent:
            continue
        counts[intent] = counts.get(intent, 0) + 1
    return counts


def _bounding_box(nodes) -> tuple[float, float, float]:
    max_x = 0.0
    max_y = 0.0
    max_z = 0.0

    for node in nodes:
        x0 = float(getattr(getattr(node, "transform", None), "x", 0.0) or 0.0)
        y0 = float(getattr(getattr(node, "transform", None), "y", 0.0) or 0.0)
        z0 = float(getattr(getattr(node, "transform", None), "z", 0.0) or 0.0)
        width, depth, height = _render_dimensions(node)
        max_x = max(max_x, x0 + width)
        max_y = max(max_y, y0 + depth)
        max_z = max(max_z, z0 + height)

    return max_x, max_z, max_y


def _render_dimensions(node) -> tuple[float, float, float]:
    role = getattr(node, "role", NodeRole.UNKNOWN)
    role_value = getattr(role, "value", role)
    width = float(getattr(node, "width", 0.0) or 0.0)
    depth = float(getattr(node, "depth", 0.0) or 0.0)
    height = float(getattr(node, "height", 0.0) or 0.0)
    thickness = float(getattr(node, "thickness", 0.0) or 0.0)

    if role_value in {"SIDE_PANEL", "DIVIDER"}:
        return thickness or 0.0, width or 0.0, height or 0.0
    if role_value in {"TOP_PANEL", "BOTTOM_PANEL", "SHELF"}:
        return width or 0.0, depth or 0.0, thickness or 0.0
    if role_value in {"BACK_PANEL", "DOOR_PANEL"}:
        return width or 0.0, thickness or 0.0, height or 0.0

    return width or 0.0, depth or 0.0, height or 0.0


def _first_thickness(nodes) -> float:
    for node in nodes:
        thickness = getattr(node, "thickness", None)
        if thickness is not None:
            return float(thickness)
    return 0.0


def _validation_status(validation_state) -> str:
    if validation_state is None:
        return "UNKNOWN"

    issues = list(getattr(validation_state, "issues", []) or [])
    if not issues:
        return "READY"

    has_errors = any(
        str(getattr(issue, "level", "") or "").upper() == "ERROR"
        for issue in issues
    )
    has_warnings = any(
        str(getattr(issue, "level", "") or "").upper() == "WARNING"
        for issue in issues
    )

    if has_errors:
        return "READY_WITH_ERRORS"
    if has_warnings:
        return "READY_WITH_WARNINGS"
    return "READY"


def _collect_warnings(validation_state, cost_summary) -> list[str]:
    warnings = []

    for issue in list(getattr(validation_state, "issues", []) or []):
        level = str(getattr(issue, "level", "") or "").upper()
        if level in {"WARNING", "ERROR"}:
            message = str(getattr(issue, "message", "") or "").strip()
            if message:
                warnings.append(message)

    if cost_summary is not None:
        for warning in list(getattr(cost_summary, "warnings", []) or []):
            warning_text = str(warning).strip()
            if warning_text and warning_text not in warnings:
                warnings.append(warning_text)

        cost_report = getattr(cost_summary, "cost_report", None)
        if cost_report is not None:
            for warning in list(getattr(cost_report, "warnings", []) or []):
                warning_text = str(warning).strip()
                if warning_text and warning_text not in warnings:
                    warnings.append(warning_text)

    return warnings


def _cost_summary(cost_summary) -> tuple[float | None, str]:
    if cost_summary is None:
        return None, ""

    total = getattr(cost_summary, "total_manufacturing_cost", None)
    currency = ""

    if total is None:
        cost_report = getattr(cost_summary, "cost_report", None)
        if cost_report is not None:
            total = getattr(cost_report, "total_cost", None)
            currency = str(getattr(cost_report, "currency", "") or "")

    if total is None:
        return None, currency

    if not currency:
        cost_report = getattr(cost_summary, "cost_report", None)
        if cost_report is not None:
            currency = str(getattr(cost_report, "currency", "") or "")

    return float(total), currency


def _has_wall_mount_data(project) -> bool:
    for attribute in (
        "wall_mount_points",
        "wall_mount_capability",
        "mounting_points",
        "suspension_hardware",
    ):
        if getattr(project, attribute, None):
            return True
    return False
