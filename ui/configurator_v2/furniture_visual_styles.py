# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Configurator V2
# Furniture Visual Styles
#
# Visual Components describe WHAT furniture element exists.
# Furniture Visual Styles describe HOW that element should appear.
#
# These are presentation-only dataclasses — no geometry, no machining
# logic, no CNC, no cost, no FreeCAD, no SceneNode.
#
# The rendering pipeline that turns these descriptors into actual
# visuals remains future work.
# ──────────────────────────────────────────────────────────────────────

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .visual_components import (
    BackPanelVisualComponent,
    DoorVisualComponent,
    DrawerVisualComponent,
    FeatureMarkerComponent,
    HardwareVisualComponent,
    PanelVisualComponent,
    VisualComponent,
)

# ── Shared descriptor ────────────────────────────────────────────────


@dataclass(frozen=True)
class MaterialVisualDescriptor:
    """Presentation-only material appearance descriptor.

    Carries colour, finish, and texture hints for a future renderer.
    No backend geometry objects or FreeCAD references.
    """

    material_name: str = ""
    finish: str = ""
    color_name: str = ""
    texture_descriptor: str = ""
    supplier: str = ""

    def __post_init__(self):
        object.__setattr__(self, "material_name", str(self.material_name))
        object.__setattr__(self, "finish", str(self.finish))
        object.__setattr__(self, "color_name", str(self.color_name))
        object.__setattr__(self, "texture_descriptor", str(self.texture_descriptor))
        object.__setattr__(self, "supplier", str(self.supplier))

    @property
    def is_empty(self) -> bool:
        return not any(
            (self.material_name, self.finish, self.color_name, self.texture_descriptor, self.supplier)
        )


@dataclass(frozen=True)
class EdgeBandVisualStyle:
    """Presentation-only edge band appearance descriptor."""

    material: str = ""
    color: str = ""
    thickness_mm: float = 0.0
    application: str = ""

    def __post_init__(self):
        object.__setattr__(self, "material", str(self.material))
        object.__setattr__(self, "color", str(self.color))
        thickness = self.thickness_mm
        if isinstance(thickness, bool) or not isinstance(thickness, (int, float)):
            thickness = 0.0
        object.__setattr__(self, "thickness_mm", float(thickness))
        object.__setattr__(self, "application", str(self.application))

    @property
    def is_empty(self) -> bool:
        return not any((self.material, self.color, self.thickness_mm, self.application))


# ── Base style ───────────────────────────────────────────────────────


@dataclass(frozen=True)
class FurnitureVisualStyle:
    """Base presentation-only style descriptor for any furniture element.

    Subclasses add domain-specific fields (door type, drawer front type,
    panel finish, hardware identifiers, etc.).

    No geometry, no machining logic, no backend references.
    """

    style_name: str = ""
    material: MaterialVisualDescriptor = field(default_factory=MaterialVisualDescriptor)
    edge_band: EdgeBandVisualStyle = field(default_factory=EdgeBandVisualStyle)

    def __post_init__(self):
        object.__setattr__(self, "style_name", str(self.style_name))
        if not isinstance(self.material, MaterialVisualDescriptor):
            object.__setattr__(self, "material", MaterialVisualDescriptor())
        if not isinstance(self.edge_band, EdgeBandVisualStyle):
            object.__setattr__(self, "edge_band", EdgeBandVisualStyle())


# ── Concrete style dataclasses ───────────────────────────────────────


@dataclass(frozen=True)
class DoorVisualStyle(FurnitureVisualStyle):
    """Presentation-only door visual style descriptor.

    Supported door types: slab, shaker, glass, framed, flush.
    Mount indicator: overlay / inset.
    Handle position: left, right, center, top, none.
    """

    door_type: str = ""
    overlay_inset: str = ""
    handle_position: str = ""

    def __post_init__(self):
        object.__setattr__(self, "door_type", str(self.door_type))
        object.__setattr__(self, "overlay_inset", str(self.overlay_inset))
        object.__setattr__(self, "handle_position", str(self.handle_position))


@dataclass(frozen=True)
class DrawerVisualStyle(FurnitureVisualStyle):
    """Presentation-only drawer visual style descriptor.

    Front types: slab front, framed front.
    Internal box indicator: bool.
    Slide type: side-mount, under-mount, center-mount.
    Handle position: left, right, center, top, none.
    """

    front_type: str = ""
    internal_box: bool = False
    slide_type: str = ""
    handle_position: str = ""

    def __post_init__(self):
        object.__setattr__(self, "front_type", str(self.front_type))
        object.__setattr__(self, "internal_box", bool(self.internal_box))
        object.__setattr__(self, "slide_type", str(self.slide_type))
        object.__setattr__(self, "handle_position", str(self.handle_position))


@dataclass(frozen=True)
class PanelVisualStyle(FurnitureVisualStyle):
    """Presentation-only panel visual style descriptor.

    Material finish: matte, gloss, textured, wood-grain, etc.
    Colour name: any human-readable colour label.
    Texture descriptor: fine, medium, coarse, smooth, brushed, etc.
    Edge banding appearance: match, contrast, none.
    """

    material_finish: str = ""
    color_name: str = ""
    texture_descriptor: str = ""
    edge_banding_appearance: str = ""

    def __post_init__(self):
        object.__setattr__(self, "material_finish", str(self.material_finish))
        object.__setattr__(self, "color_name", str(self.color_name))
        object.__setattr__(self, "texture_descriptor", str(self.texture_descriptor))
        object.__setattr__(self, "edge_banding_appearance", str(self.edge_banding_appearance))


@dataclass(frozen=True)
class BackPanelVisualStyle(FurnitureVisualStyle):
    """Presentation-only back-panel visual style descriptor.

    Thin panel: standard thin hardboard / MDF back.
    Recessed panel: inset into a groove.
    Groove indicator: single, double, none.
    """

    thin_panel: bool = False
    recessed_panel: bool = False
    groove_indicator: str = ""

    def __post_init__(self):
        object.__setattr__(self, "thin_panel", bool(self.thin_panel))
        object.__setattr__(self, "recessed_panel", bool(self.recessed_panel))
        object.__setattr__(self, "groove_indicator", str(self.groove_indicator))


@dataclass(frozen=True)
class HardwareVisualStyle(FurnitureVisualStyle):
    """Presentation-only hardware visual style descriptor.

    Each field names a hardware component type found on the furniture
    element. Values are descriptive strings (model, finish, type).
    """

    hinge: str = ""
    handle: str = ""
    drawer_slide: str = ""
    shelf_pin: str = ""
    minifix: str = ""
    confirmat: str = ""

    def __post_init__(self):
        object.__setattr__(self, "hinge", str(self.hinge))
        object.__setattr__(self, "handle", str(self.handle))
        object.__setattr__(self, "drawer_slide", str(self.drawer_slide))
        object.__setattr__(self, "shelf_pin", str(self.shelf_pin))
        object.__setattr__(self, "minifix", str(self.minifix))
        object.__setattr__(self, "confirmat", str(self.confirmat))


@dataclass(frozen=True)
class FeatureMarkerVisualStyle(FurnitureVisualStyle):
    """Presentation-only feature marker visual style descriptor.

    Each field names a machining feature type. Values are descriptive
    strings (depth, diameter, position reference, etc.).

    Note: ``edge_band_feature`` is a machining feature name, not the
    EdgeBandVisualStyle from the base class (which describes the edge
    banding *material*).
    """

    drilling: str = ""
    groove: str = ""
    cutout: str = ""
    edge_band_feature: str = ""
    machining_marker: str = ""

    def __post_init__(self):
        object.__setattr__(self, "drilling", str(self.drilling))
        object.__setattr__(self, "groove", str(self.groove))
        object.__setattr__(self, "cutout", str(self.cutout))
        object.__setattr__(self, "edge_band_feature", str(self.edge_band_feature))
        object.__setattr__(self, "machining_marker", str(self.machining_marker))


# ── Builder ──────────────────────────────────────────────────────────


def _parse_metadata(
    component: VisualComponent,
) -> dict[str, str]:
    """Extract a key-value lookup from the component's display_metadata."""
    lookup: dict[str, str] = {}
    for key, value in component.display_metadata:
        lookup[key.lower().replace(" ", "_")] = value
    return lookup


def _build_material(component: VisualComponent, meta: dict[str, str]) -> MaterialVisualDescriptor:
    return MaterialVisualDescriptor(
        material_name=component.material_name,
        finish=meta.get("finish", ""),
        color_name=meta.get("color_name", meta.get("color", "")),
        texture_descriptor=meta.get("texture", meta.get("texture_descriptor", "")),
        supplier=meta.get("supplier", ""),
    )


def _build_edge_band(meta: dict[str, str]) -> EdgeBandVisualStyle:
    thickness_raw = meta.get("edge_thickness", meta.get("edge_thickness_mm", "0"))
    try:
        thickness = float(thickness_raw)
    except (ValueError, TypeError):
        thickness = 0.0
    return EdgeBandVisualStyle(
        material=meta.get("edge_material", ""),
        color=meta.get("edge_color", ""),
        thickness_mm=thickness,
        application=meta.get("edge_application", ""),
    )


def _build_door_style(component: VisualComponent) -> DoorVisualStyle:
    meta = _parse_metadata(component)
    return DoorVisualStyle(
        style_name=meta.get("door_style", "slab"),
        material=_build_material(component, meta),
        edge_band=_build_edge_band(meta),
        door_type=meta.get("door_style", meta.get("door_type", "slab")),
        overlay_inset=meta.get("mount", meta.get("overlay_inset", "overlay")),
        handle_position=meta.get("handle_position", ""),
    )


def _build_drawer_style(component: VisualComponent) -> DrawerVisualStyle:
    meta = _parse_metadata(component)
    internal_box_val = meta.get("internal_box", meta.get("box", "false"))
    return DrawerVisualStyle(
        style_name=meta.get("drawer_style", "slab"),
        material=_build_material(component, meta),
        edge_band=_build_edge_band(meta),
        front_type=meta.get("front_type", meta.get("drawer_style", "slab")),
        internal_box=internal_box_val.lower() in ("true", "yes", "1"),
        slide_type=meta.get("slide_type", ""),
        handle_position=meta.get("handle_position", ""),
    )


def _build_panel_style(component: VisualComponent) -> PanelVisualStyle:
    meta = _parse_metadata(component)
    return PanelVisualStyle(
        style_name="panel",
        material=_build_material(component, meta),
        edge_band=_build_edge_band(meta),
        material_finish=meta.get("finish", ""),
        color_name=meta.get("color_name", meta.get("color", "")),
        texture_descriptor=meta.get("texture", meta.get("texture_descriptor", "")),
        edge_banding_appearance=meta.get("edge_appearance", meta.get("edge_banding_appearance", "")),
    )


def _build_back_panel_style(component: VisualComponent) -> BackPanelVisualStyle:
    meta = _parse_metadata(component)
    thin_val = meta.get("thin_panel", meta.get("thin", "true"))
    recessed_val = meta.get("recessed_panel", meta.get("recessed", "false"))
    return BackPanelVisualStyle(
        style_name=meta.get("back_panel_style", "standard"),
        material=_build_material(component, meta),
        edge_band=_build_edge_band(meta),
        thin_panel=thin_val.lower() in ("true", "yes", "1"),
        recessed_panel=recessed_val.lower() in ("true", "yes", "1"),
        groove_indicator=meta.get("groove", meta.get("groove_indicator", "")),
    )


def _build_hardware_style(component: VisualComponent) -> HardwareVisualStyle:
    meta = _parse_metadata(component)
    return HardwareVisualStyle(
        style_name="hardware",
        material=_build_material(component, meta),
        edge_band=_build_edge_band(meta),
        hinge=meta.get("hinge", ""),
        handle=meta.get("handle", ""),
        drawer_slide=meta.get("slide", meta.get("drawer_slide", "")),
        shelf_pin=meta.get("shelf_pin", ""),
        minifix=meta.get("minifix", ""),
        confirmat=meta.get("confirmat", ""),
    )


def _build_feature_marker_style(component: VisualComponent) -> FeatureMarkerVisualStyle:
    meta = _parse_metadata(component)
    return FeatureMarkerVisualStyle(
        style_name=meta.get("feature_type", "marker"),
        material=_build_material(component, meta),
        edge_band=_build_edge_band(meta),
        drilling=meta.get("drilling", meta.get("drill", "")),
        groove=meta.get("groove", ""),
        cutout=meta.get("cutout", ""),
        edge_band_feature=meta.get("edge_band_feature", meta.get("edge_band", "")),
        machining_marker=meta.get("machining_marker", meta.get("marker", "")),
    )


_STYLE_BUILDERS: dict[type[VisualComponent], callable] = {
    DoorVisualComponent: _build_door_style,
    DrawerVisualComponent: _build_drawer_style,
    PanelVisualComponent: _build_panel_style,
    BackPanelVisualComponent: _build_back_panel_style,
    HardwareVisualComponent: _build_hardware_style,
    FeatureMarkerComponent: _build_feature_marker_style,
}


def build_furniture_visual_style(
    component: VisualComponent,
) -> FurnitureVisualStyle | None:
    """Build a FurnitureVisualStyle from a VisualComponent.

    The style descriptor is derived entirely from the component's
    display_metadata and material_name — no backend objects, no geometry,
    no FreeCAD references.

    Returns None if the component type has no registered style builder.
    """
    if not isinstance(component, VisualComponent):
        raise TypeError("component must be a VisualComponent")

    builder = _STYLE_BUILDERS.get(type(component))
    if builder is None:
        # Return a base style for unregistered component types
        return FurnitureVisualStyle(
            style_name="generic",
            material=_build_material(component, _parse_metadata(component)),
            edge_band=_build_edge_band(_parse_metadata(component)),
        )
    return builder(component)


def apply_furniture_visual_styles(
    components: tuple[VisualComponent, ...],
) -> tuple[FurnitureVisualStyle, ...]:
    """Build visual styles for a sequence of VisualComponents.

    Maintains one-to-one correspondence with the input components.
    """
    return tuple(build_furniture_visual_style(c) for c in components)


# ── Style descriptor helpers ─────────────────────────────────────────


def style_descriptor_pairs(
    style: FurnitureVisualStyle | None,
) -> tuple[tuple[str, str], ...]:
    """Flatten a FurnitureVisualStyle into display metadata key-value pairs.

    Returns an empty tuple when style is None or has no meaningful data.
    """
    if style is None:
        return ()

    pairs: list[tuple[str, str]] = []

    if style.style_name:
        pairs.append(("style_name", style.style_name))

    if style.material and not style.material.is_empty:
        m = style.material
        if m.material_name:
            pairs.append(("style_material", m.material_name))
        if m.finish:
            pairs.append(("style_finish", m.finish))
        if m.color_name:
            pairs.append(("style_color", m.color_name))
        if m.texture_descriptor:
            pairs.append(("style_texture", m.texture_descriptor))
        if m.supplier:
            pairs.append(("style_supplier", m.supplier))

    if style.edge_band and not style.edge_band.is_empty:
        e = style.edge_band
        if e.material:
            pairs.append(("edge_band_material", e.material))
        if e.color:
            pairs.append(("edge_band_color", e.color))
        if e.thickness_mm:
            pairs.append(("edge_band_thickness_mm", f"{e.thickness_mm:.1f}"))
        if e.application:
            pairs.append(("edge_band_application", e.application))

    # Subclass-specific fields
    if isinstance(style, DoorVisualStyle):
        if style.door_type:
            pairs.append(("door_type", style.door_type))
        if style.overlay_inset:
            pairs.append(("mount", style.overlay_inset))
        if style.handle_position:
            pairs.append(("handle_position", style.handle_position))

    elif isinstance(style, DrawerVisualStyle):
        if style.front_type:
            pairs.append(("front_type", style.front_type))
        pairs.append(("internal_box", "yes" if style.internal_box else "no"))
        if style.slide_type:
            pairs.append(("slide_type", style.slide_type))
        if style.handle_position:
            pairs.append(("handle_position", style.handle_position))

    elif isinstance(style, PanelVisualStyle):
        if style.material_finish:
            pairs.append(("material_finish", style.material_finish))
        if style.color_name:
            pairs.append(("color_name", style.color_name))
        if style.texture_descriptor:
            pairs.append(("texture", style.texture_descriptor))
        if style.edge_banding_appearance:
            pairs.append(("edge_banding_appearance", style.edge_banding_appearance))

    elif isinstance(style, BackPanelVisualStyle):
        pairs.append(("thin_panel", "yes" if style.thin_panel else "no"))
        pairs.append(("recessed_panel", "yes" if style.recessed_panel else "no"))
        if style.groove_indicator:
            pairs.append(("groove", style.groove_indicator))

    elif isinstance(style, HardwareVisualStyle):
        if style.hinge:
            pairs.append(("hinge", style.hinge))
        if style.handle:
            pairs.append(("handle", style.handle))
        if style.drawer_slide:
            pairs.append(("drawer_slide", style.drawer_slide))
        if style.shelf_pin:
            pairs.append(("shelf_pin", style.shelf_pin))
        if style.minifix:
            pairs.append(("minifix", style.minifix))
        if style.confirmat:
            pairs.append(("confirmat", style.confirmat))

    elif isinstance(style, FeatureMarkerVisualStyle):
        if style.drilling:
            pairs.append(("drilling", style.drilling))
        if style.groove:
            pairs.append(("groove", style.groove))
        if style.cutout:
            pairs.append(("cutout", style.cutout))
        if style.edge_band_feature:
            pairs.append(("edge_band_feature", style.edge_band_feature))
        if style.machining_marker:
            pairs.append(("machining_marker", style.machining_marker))

    return tuple(pairs)


# ── Summary label ────────────────────────────────────────────────────


def style_summary_label(style: FurnitureVisualStyle | None) -> str:
    """Return a single-line human-readable summary of a visual style."""
    if style is None:
        return "No style"

    label = style.style_name or "Unnamed"
    if isinstance(style, DoorVisualStyle):
        parts = [style.door_type or label]
        if style.overlay_inset:
            parts.append(style.overlay_inset)
        if style.material.material_name:
            parts.append(style.material.material_name)
        return " | ".join(parts)
    elif isinstance(style, DrawerVisualStyle):
        parts = [style.front_type or label]
        if style.slide_type:
            parts.append(style.slide_type)
        if style.material.material_name:
            parts.append(style.material.material_name)
        return " | ".join(parts)
    elif isinstance(style, PanelVisualStyle):
        parts = [style.material_finish or style.material.material_name or label]
        if style.color_name:
            parts.append(style.color_name)
        if style.edge_banding_appearance:
            parts.append(style.edge_banding_appearance)
        return " | ".join(parts)
    elif isinstance(style, BackPanelVisualStyle):
        parts = ["Back panel"]
        if style.thin_panel:
            parts.append("thin")
        if style.recessed_panel:
            parts.append("recessed")
        if style.groove_indicator:
            parts.append(style.groove_indicator)
        return " | ".join(parts)
    elif isinstance(style, HardwareVisualStyle):
        parts = ["Hardware"]
        if style.hinge:
            parts.append(style.hinge)
        if style.handle:
            parts.append(style.handle)
        if style.drawer_slide:
            parts.append(style.drawer_slide)
        return " | ".join(parts)
    elif isinstance(style, FeatureMarkerVisualStyle):
        parts = ["Marker"]
        if style.drilling:
            parts.append(f"drill:{style.drilling}")
        if style.groove:
            parts.append(f"groove:{style.groove}")
        if style.cutout:
            parts.append(f"cutout:{style.cutout}")
        if style.edge_band_feature:
            parts.append(f"eb:{style.edge_band_feature}")
        return " | ".join(parts)
    return label


__all__ = [
    "FurnitureVisualStyle",
    "DoorVisualStyle",
    "DrawerVisualStyle",
    "PanelVisualStyle",
    "BackPanelVisualStyle",
    "EdgeBandVisualStyle",
    "HardwareVisualStyle",
    "FeatureMarkerVisualStyle",
    "MaterialVisualDescriptor",
    "build_furniture_visual_style",
    "apply_furniture_visual_styles",
    "style_descriptor_pairs",
    "style_summary_label",
]
