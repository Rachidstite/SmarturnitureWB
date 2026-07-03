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

    return VisualMetadata(
        edge_banding=edge_banding,
        drill_holes=drill_holes,
        grooves=grooves,
        hardware_markers=hardware_markers,
        material_label=material_label,
        finish_label=str(finish_label or ""),
    )


def _panel_identity(node) -> str:
    return str(getattr(getattr(node, "identity", None), "key", "") or "")


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
