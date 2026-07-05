from dataclasses import dataclass, field


@dataclass(frozen=True)
class EdgeBandVisual:
    side: str = ""
    banding: str = ""
    label: str = ""


@dataclass(frozen=True)
class DrillHoleVisual:
    panel_identity: str = ""
    operation_type: str = ""
    face: str = ""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    diameter: float = 0.0
    depth: float = 0.0
    axis: str = "Z"
    is_through: bool = False
    source_operation_reference: str = ""
    hardware_intent: str = ""


@dataclass(frozen=True)
class GrooveVisual:
    panel_identity: str = ""
    face: str = "BACK"
    depth: float = 0.0
    label: str = ""
    source_rule: str = ""


@dataclass(frozen=True)
class HardwareMarkerVisual:
    panel_identity: str = ""
    sku: str = ""
    quantity: int = 0
    hardware_category: str = ""
    label: str = ""
    component_reference: tuple[str, ...] = field(default_factory=tuple)
    cabinet_reference: tuple[str, ...] = field(default_factory=tuple)
    source_operation_references: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class VisualMetadata:
    edge_banding: tuple[EdgeBandVisual, ...] = field(default_factory=tuple)
    drill_holes: tuple[DrillHoleVisual, ...] = field(default_factory=tuple)
    grooves: tuple[GrooveVisual, ...] = field(default_factory=tuple)
    hardware_markers: tuple[HardwareMarkerVisual, ...] = field(default_factory=tuple)
    material_label: str = ""
    finish_label: str = ""
    # ── Manufacturing feature extensions (HFG-2) ─────────────────
    minifix_holes: tuple[DrillHoleVisual, ...] = field(default_factory=tuple)
    confirmat_holes: tuple[DrillHoleVisual, ...] = field(default_factory=tuple)
    shelf_pin_holes: tuple[DrillHoleVisual, ...] = field(default_factory=tuple)
    drawer_slide_holes: tuple[DrillHoleVisual, ...] = field(default_factory=tuple)
    hinge_cup_holes: tuple[DrillHoleVisual, ...] = field(default_factory=tuple)
    hinge_plate_positions: tuple[DrillHoleVisual, ...] = field(default_factory=tuple)
    screw_holes: tuple[DrillHoleVisual, ...] = field(default_factory=tuple)

@dataclass
class DoorMetadata:
    door_type: str
    hinge_side: str = "LEFT"
    layer: int = 0
    cnc_enabled: bool = False

@dataclass
class DrawerMetadata:
    drawer_type: str
    box_w: float; box_h: float; box_d: float
    box_x: float; box_y: float; box_z: float
    bottom_thickness: float

@dataclass
class EngineeringDrawerFaceMetadata:
    source_rule: str
    section_index: int
    drawer_index: int

@dataclass
class BackPanelMetadata:
    section_index: int
    section_label: str
    is_section_back: bool
    groove_depth: float
    back_offset: float
    extends_into_groove: bool
    source_rule: str


# ── Intent constants (mirrors visible_geometry_plan usage) ──────────

_INTENT_MINIFIX = "INTENT_MINIFIX_15"
_INTENT_CONFIRMAT = "INTENT_CONFIRMAT_50"
_INTENT_SHELF_PIN = "INTENT_SHELF_PIN"
_INTENT_DRAWER_SLIDE = "INTENT_DRAWER_SLIDE"
_INTENT_HINGE = "INTENT_HINGE"
_INTENT_SCREW = "INTENT_SCREW"
_INTENT_PANEL_SCREW = "INTENT_PANEL_SCREW"


# ── Public builder ───────────────────────────────────────────────

def build_visual_metadata(
    node,
    *,
    cnc_report=None,
    manufacturing_edge_report=None,
    hardware_bom=None,
    assembly_report=None,
) -> VisualMetadata:
    panel_identity = _panel_identity(node)
    edge_banding = _edge_banding_from_report(
        panel_identity,
        manufacturing_edge_report,
    )
    drill_holes = _drill_holes_from_cnc(panel_identity, cnc_report)
    grooves = _grooves_from_node(panel_identity, node)
    hardware_markers = _hardware_markers_from_reports(
        panel_identity,
        hardware_bom=hardware_bom,
        assembly_report=assembly_report,
    )
    material_label = str(getattr(node, "material", "") or "")
    finish_label = _metadata_value(getattr(node, "metadata", None), "finish_label", "")

    # ── Manufacturing feature extraction (HFG-2) ────────────────
    minifix_holes = _minifix_holes_from_node(node, panel_identity)
    confirmat_holes = _confirmat_holes_from_node(node, panel_identity)
    shelf_pin_holes = _shelf_pin_holes_from_node(node, panel_identity)
    drawer_slide_holes = _drawer_slide_holes_from_node(node, panel_identity)
    hinge_cup_holes = _hinge_cup_holes_from_node(node, panel_identity)
    hinge_plate_positions = _hinge_plate_from_node(node, panel_identity)
    screw_holes = _screw_holes_from_node(node, panel_identity)

    return VisualMetadata(
        edge_banding=edge_banding,
        drill_holes=drill_holes,
        grooves=grooves,
        hardware_markers=hardware_markers,
        material_label=material_label,
        finish_label=str(finish_label or ""),
        minifix_holes=minifix_holes,
        confirmat_holes=confirmat_holes,
        shelf_pin_holes=shelf_pin_holes,
        drawer_slide_holes=drawer_slide_holes,
        hinge_cup_holes=hinge_cup_holes,
        hinge_plate_positions=hinge_plate_positions,
        screw_holes=screw_holes,
    )


# ── Panel identity helper ────────────────────────────────────────

def _panel_identity(node) -> str:
    return str(getattr(getattr(node, "identity", None), "key", "") or "")


# ── Edge banding extraction ─────────────────────────────────────

def _edge_banding_from_report(panel_identity: str, manufacturing_edge_report) -> tuple[EdgeBandVisual, ...]:
    rows = getattr(manufacturing_edge_report, "items", None) or []
    visuals = []
    for row in rows:
        if panel_identity and str(_metadata_value(row, "panel_identity", "") or "") != panel_identity:
            continue
        edge = str(_metadata_value(row, "edge", "") or "").upper()
        banding = str(_metadata_value(row, "banding", "") or "")
        if not edge and not banding:
            continue
        visuals.append(
            EdgeBandVisual(
                side=edge,
                banding=banding,
                label=f"{edge} edge: {banding}" if edge else banding,
            )
        )
    return tuple(visuals)


# ── Drill hole extraction (generic) ─────────────────────────────

def _drill_holes_from_cnc(panel_identity: str, cnc_report) -> tuple[DrillHoleVisual, ...]:
    rows = getattr(cnc_report, "rows", None) or []
    visuals = []
    for row in rows:
        if panel_identity and str(getattr(row, "panel_identity", "") or "") != panel_identity:
            continue
        if str(getattr(row, "operation_type", "") or "").upper() != "DRILL":
            continue
        visuals.append(
            DrillHoleVisual(
                panel_identity=str(getattr(row, "panel_identity", "") or ""),
                operation_type=str(getattr(row, "operation_type", "") or ""),
                face=str(getattr(row, "face", "") or ""),
                x=float(getattr(row, "x", 0.0) or 0.0),
                y=float(getattr(row, "y", 0.0) or 0.0),
                z=float(getattr(row, "z", 0.0) or 0.0),
                diameter=float(getattr(row, "diameter", 0.0) or 0.0),
                depth=float(getattr(row, "depth", 0.0) or 0.0),
                axis=str(getattr(row, "axis", "Z") or "Z"),
                is_through=bool(getattr(row, "is_through", False)),
                source_operation_reference=str(
                    getattr(row, "source_operation_reference", "") or ""
                ),
            )
        )
    return tuple(visuals)


# ── Groove extraction ──────────────────────────────────────────

def _grooves_from_node(panel_identity: str, node) -> tuple[GrooveVisual, ...]:
    metadata = getattr(node, "metadata", None)
    groove_depth = float(_metadata_value(metadata, "groove_depth", 0.0) or 0.0)
    if groove_depth <= 0.0:
        return ()

    return (
        GrooveVisual(
            panel_identity=panel_identity,
            face="BACK",
            depth=groove_depth,
            label="Back panel groove",
            source_rule=str(_metadata_value(metadata, "source_rule", "") or ""),
        ),
    )


# ── Hardware marker extraction ─────────────────────────────────

def _hardware_markers_from_reports(
    panel_identity: str,
    *,
    hardware_bom=None,
    assembly_report=None,
) -> tuple[HardwareMarkerVisual, ...]:
    markers = []

    for row in getattr(hardware_bom, "bom_rows", None) or []:
        component_reference = tuple(getattr(row, "component_reference", ()) or ())
        cabinet_reference = tuple(getattr(row, "cabinet_reference", ()) or ())
        if panel_identity and panel_identity not in component_reference and panel_identity not in cabinet_reference:
            continue
        markers.append(
            HardwareMarkerVisual(
                panel_identity=panel_identity,
                sku=str(getattr(row, "sku", "") or getattr(row, "hardware_sku", "") or ""),
                quantity=int(getattr(row, "quantity", 0) or 0),
                hardware_category=str(getattr(row, "hardware_category", "") or ""),
                label=str(getattr(row, "description", "") or ""),
                component_reference=component_reference,
                cabinet_reference=cabinet_reference,
                source_operation_references=tuple(
                    getattr(row, "source_operation_references", ()) or ()
                ),
            )
        )

    if markers or assembly_report is None:
        return tuple(markers)

    for row in getattr(assembly_report, "rows", None) or []:
        component_reference = tuple(getattr(row, "component_reference", ()) or ())
        cabinet_reference = tuple(getattr(row, "cabinet_reference", ()) or ())
        if panel_identity and panel_identity not in component_reference and panel_identity not in cabinet_reference:
            continue
        markers.append(
            HardwareMarkerVisual(
                panel_identity=panel_identity,
                sku=str(getattr(row, "hardware_required", "") or ""),
                quantity=int(getattr(row, "hardware_quantity", 0) or 0),
                hardware_category=str(getattr(row, "assembly_group", "") or ""),
                label=", ".join(str(note) for note in (getattr(row, "assembly_notes", ()) or ())),
                component_reference=component_reference,
                cabinet_reference=cabinet_reference,
                source_operation_references=tuple(
                    getattr(row, "source_operation_references", ()) or ()
                ),
            )
        )

    return tuple(markers)


def _metadata_value(metadata, key: str, default):
    if isinstance(metadata, dict):
        return metadata.get(key, default)
    if metadata is None:
        return default
    return getattr(metadata, key, default)


# ── Manufacturing feature extraction helpers (HFG-2) ──────────────

# These functions read from the node's machining_ops list to extract
# classified drilling features. Each machining operation carries a
# metadata dict with a "hardware_intent" key. The classification is
# performed by matching the intent string — no business logic is
# duplicated because the intent was assigned by the manufacturing
# compiler (domain/manufacturing_compiler.py), not re-derived here.


def _node_role_name(node) -> str:
    """Get the role name string from a node."""
    role = getattr(node, "role", None)
    if role is None:
        return ""
    return str(getattr(role, "value", getattr(role, "name", str(role)))).upper()


def _op_intent(op) -> str:
    """Extract hardware_intent from an operation's metadata."""
    metadata = getattr(op, "metadata", None) or {}
    if isinstance(metadata, dict):
        return str(metadata.get("hardware_intent", "") or "")
    return str(getattr(metadata, "hardware_intent", "") or "")


def _hole_visual_from_op(op, panel_identity: str, intent: str) -> DrillHoleVisual:
    """Build a DrillHoleVisual from a machining operation."""
    return DrillHoleVisual(
        panel_identity=panel_identity,
        operation_type=str(getattr(op, "op_type", "") or getattr(op, "operation_type", "") or ""),
        face=str(getattr(op, "face", "") or ""),
        x=float(getattr(op, "local_x", getattr(op, "x", 0.0)) or 0.0),
        y=float(getattr(op, "local_y", getattr(op, "y", 0.0)) or 0.0),
        z=float(getattr(op, "z", 0.0) or 0.0),
        diameter=float(getattr(op, "diameter", 0.0) or 0.0),
        depth=float(getattr(op, "depth", 0.0) or 0.0),
        axis=str(getattr(op, "axis", "Z") or "Z"),
        is_through=bool(getattr(op, "is_through", False)),
        source_operation_reference=str(getattr(op, "source", "") or getattr(op, "source_operation_reference", "") or ""),
        hardware_intent=intent,
    )


def _filter_ops_by_intent(node, intent: str) -> list:
    """Filter machining operations by hardware_intent."""
    results = []
    for op in list(getattr(node, "machining_ops", []) or []):
        if _op_intent(op).upper() != intent.upper():
            continue
        results.append(op)
    return results


def _minifix_holes_from_node(node, panel_identity: str) -> tuple[DrillHoleVisual, ...]:
    """Extract minifix drilling positions from node's machining operations.

    References: visible_geometry_plan._minifix_features()
    """
    ops = _filter_ops_by_intent(node, _INTENT_MINIFIX)
    return tuple(
        _hole_visual_from_op(op, panel_identity, _INTENT_MINIFIX)
        for op in ops
    )


def _confirmat_holes_from_node(node, panel_identity: str) -> tuple[DrillHoleVisual, ...]:
    """Extract confirmat drilling positions.

    References: visible_geometry_plan._confirmat_features()
    """
    ops = _filter_ops_by_intent(node, _INTENT_CONFIRMAT)
    return tuple(
        _hole_visual_from_op(op, panel_identity, _INTENT_CONFIRMAT)
        for op in ops
    )


def _shelf_pin_holes_from_node(node, panel_identity: str) -> tuple[DrillHoleVisual, ...]:
    """Extract shelf pin hole positions.

    References: visible_geometry_plan._side_panel_drilling_features()
    """
    ops = _filter_ops_by_intent(node, _INTENT_SHELF_PIN)
    return tuple(
        _hole_visual_from_op(op, panel_identity, _INTENT_SHELF_PIN)
        for op in ops
    )


def _drawer_slide_holes_from_node(node, panel_identity: str) -> tuple[DrillHoleVisual, ...]:
    """Extract drawer slide hole positions.

    References: visible_geometry_plan._drawer_slide_features()
    """
    ops = _filter_ops_by_intent(node, _INTENT_DRAWER_SLIDE)
    return tuple(
        _hole_visual_from_op(op, panel_identity, _INTENT_DRAWER_SLIDE)
        for op in ops
    )


def _hinge_cup_holes_from_node(node, panel_identity: str) -> tuple[DrillHoleVisual, ...]:
    """Extract hinge cup drilling positions (on DOOR_PANEL nodes).

    References: visible_geometry_plan._hinge_cup_features()
    """
    role = _node_role_name(node)
    if role != "DOOR_PANEL":
        return ()
    ops = _filter_ops_by_intent(node, _INTENT_HINGE)
    return tuple(
        _hole_visual_from_op(op, panel_identity, _INTENT_HINGE)
        for op in ops
    )


def _hinge_plate_from_node(node, panel_identity: str) -> tuple[DrillHoleVisual, ...]:
    """Extract hinge plate positions (on SIDE_PANEL or DIVIDER nodes).

    References: visible_geometry_plan._hinge_plate_features()
    """
    role = _node_role_name(node)
    if role not in ("SIDE_PANEL", "DIVIDER"):
        return ()
    ops = _filter_ops_by_intent(node, _INTENT_HINGE)
    return tuple(
        _hole_visual_from_op(op, panel_identity, _INTENT_HINGE)
        for op in ops
    )


def _screw_holes_from_node(node, panel_identity: str) -> tuple[DrillHoleVisual, ...]:
    """Extract screw drilling positions.

    References: visible_geometry_plan._screw_features()
    """
    ops = []
    for op in list(getattr(node, "machining_ops", []) or []):
        intent = _op_intent(op).upper()
        if intent in (_INTENT_SCREW.upper(), _INTENT_PANEL_SCREW.upper()):
            ops.append(op)
    return tuple(
        _hole_visual_from_op(op, panel_identity, intent)
        for op in ops
        for intent in [_op_intent(op)]
    )
