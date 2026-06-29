from engine.geometry_engine import GeometryEngine
from core.material_manager import MaterialManager
from scene_graph.node import SceneNode
from scene_graph.scene_graph import SceneGraph
from shared.identity import PanelIdentity, SemanticRole, normalize_identity_part
from shared.roles import NodeRole
from manufacturing.edge_spec import EdgeBandRegistry
from scene_graph.metadata import BackPanelMetadata, DoorMetadata, DrawerMetadata
from domain.back_panel_engine import BackPanelRule
from domain.furniture_construction_model import CabinetConstructionModel
from domain.base_cabinet_engineering_model import (
    BackPanelInstallationMode,
    EngineeringDividerPlacement,
    EngineeringShelfPlacement,
    BaseCabinetEngineeringModel,
)


def resolve_back_panel_geometry(cabinet, mat: MaterialManager, section_index: int, section):
    params = cabinet.params
    back_type = str(getattr(params, "back_panel_type", "REAR") or "REAR").upper()
    if back_type == "NONE":
        return None

    back_rule = BackPanelRule()
    inner_x = getattr(section, "inner_x", getattr(section, "origin_x", mat.mdf_thickness))
    inner_width = getattr(section, "inner_width", getattr(section, "width", params.width - (2 * mat.mdf_thickness)))
    base_height = getattr(params, "base_height", 0.0)
    thickness = getattr(mat, "back_thickness", back_rule.thickness)

    if back_type == "GROOVE":
        groove_offset = back_rule.groove_offset
        return {
            "width": inner_width,
            "depth": thickness,
            "height": params.height - base_height - (2 * groove_offset),
            "x": inner_x - back_rule.groove_depth,
            "y": params.depth - groove_offset - thickness,
            "z": base_height + groove_offset,
            "metadata": BackPanelMetadata(
                section_index=section_index,
                section_label=f"SEC-{section_index + 1}",
                is_section_back=True,
                groove_depth=back_rule.groove_depth,
                back_offset=groove_offset,
                extends_into_groove=True,
                source_rule="BackPanelRule:GROOVE",
            ),
        }

    return {
        "width": inner_width,
        "depth": thickness,
        "height": params.height - base_height - (2 * getattr(mat, "mdf_thickness", back_rule.thickness)),
        "x": inner_x,
        "y": params.depth - thickness,
        "z": base_height + getattr(mat, "mdf_thickness", back_rule.thickness),
        "metadata": BackPanelMetadata(
            section_index=section_index,
            section_label=f"SEC-{section_index + 1}",
            is_section_back=True,
            groove_depth=back_rule.groove_depth,
            back_offset=thickness,
            extends_into_groove=False,
            source_rule="BackPanelRule:REAR",
        ),
    }

class SceneGraphBuilder:
    def __init__(self, cabinet, mat: MaterialManager, cabinet_id: str = None):
        self.cabinet = cabinet
        self.mat = mat
        self.graph = SceneGraph()
        self.cabinet_id = self._resolve_cabinet_id(cabinet_id)

    def _resolve_cabinet_id(self, cabinet_id: str = None) -> str:
        if cabinet_id:
            return normalize_identity_part(cabinet_id)
        params = self.cabinet.params
        width = int(round(params.width))
        height = int(round(params.height))
        depth = int(round(params.depth))
        sec_count = int(params.sec_count)
        return normalize_identity_part(f"CAB-{width}x{height}x{depth}-S{sec_count}")

    def build(self, geo: GeometryEngine) -> SceneGraph:
        engineering_model = getattr(self.cabinet, "engineering_model", None)
        if isinstance(engineering_model, BaseCabinetEngineeringModel):
            return self._build_from_engineering_model(engineering_model)

        construction_model = getattr(self.cabinet, "construction_model", None)
        if isinstance(construction_model, CabinetConstructionModel):
            return self._build_from_construction_model(construction_model)

        T = self.mat.mdf_thickness; base_H = self.cabinet.params.base_height
        W = self.cabinet.params.width; D = self.cabinet.params.depth; H = self.cabinet.params.height

        # --- الهيكل الأساسي (كما هو) ---
        self._add(SceneNode(PanelIdentity.make_side(self.cabinet_id, "LEFT"),
                            T, D, H - T, 0, 0, 0, group="Carcass", role=NodeRole.SIDE_PANEL, thickness=T))
        self._add(SceneNode(PanelIdentity.make_side(self.cabinet_id, "RIGHT"),
                            T, D, H - T, W - T, 0, 0, group="Carcass", role=NodeRole.SIDE_PANEL, thickness=T))
        top = geo.resolved_top
        self._add(SceneNode(PanelIdentity(self.cabinet_id, "SEC-TOP", SemanticRole.TOP),
                            top.width, top.depth, top.thickness, top.x, top.y, top.z,
                            group="Carcass", role=NodeRole.TOP_PANEL, thickness=top.thickness))
        inner_W = W - 2 * T
        self._add(SceneNode(PanelIdentity(self.cabinet_id, "SEC-BOTTOM", SemanticRole.BOTTOM),
                            inner_W, D, T, T, 0, base_H, group="Carcass", role=NodeRole.BOTTOM_PANEL, thickness=T))
        if base_H > 0:
            self._add(SceneNode(PanelIdentity(self.cabinet_id, "STRUCTURE", SemanticRole.PLINTH, 1),
                                inner_W, T, base_H, T, 20, 0, group="Carcass", role=NodeRole.PLINTH, thickness=T))
            self._add(SceneNode(PanelIdentity(self.cabinet_id, "STRUCTURE", SemanticRole.PLINTH, 2),
                                inner_W, T, base_H, T, D - 20 - self.mat.back_thickness - T, 0,
                                group="Carcass", role=NodeRole.PLINTH, thickness=T))

        for i, r in enumerate(geo.resolved_sections):
            back_geometry = resolve_back_panel_geometry(
                self.cabinet,
                self.mat,
                i,
                r,
            )
            if back_geometry is None:
                continue

            self._add(SceneNode(
                PanelIdentity(self.cabinet_id, f"SEC-{i+1}", SemanticRole.BACK, 1),
                back_geometry["width"],
                back_geometry["depth"],
                back_geometry["height"],
                back_geometry["x"],
                back_geometry["y"],
                back_geometry["z"],
                group="Carcass",
                role=NodeRole.BACK_PANEL,
                metadata=back_geometry["metadata"],
                thickness=back_geometry["depth"],
            ))
            print(
                f"[SECTION {i+1}] "
                f"shelves={len(r.shelves)} "
                f"drawers={len(r.drawers)} "
                f"doors={len(r.doors)}"
            )

            for j, shelf in enumerate(r.shelves):
                self._add(SceneNode(PanelIdentity.make_shelf(self.cabinet_id, i, j),
                                    shelf.width, shelf.depth, T, shelf.x, shelf.y, shelf.z,
                                    group="Shelves", role=NodeRole.SHELF, thickness=T))
            for j, drawer in enumerate(r.drawers):
                # Typed Metadata
                meta = DrawerMetadata(
                    drawer_type=self.cabinet.sections[i].config.drawer_type,
                    box_w=drawer.box_w, box_h=drawer.box_h, box_d=drawer.box_d,
                    box_x=drawer.box_x, box_y=drawer.box_y, box_z=drawer.box_z,
                    bottom_thickness=drawer.bottom_thickness
                )
                self._add(SceneNode(PanelIdentity.make_drawer_face(self.cabinet_id, i, j),
                                    drawer.face_w, self.mat.mdf_thickness, drawer.face_h,
                                    drawer.face_x, drawer.face_y, drawer.face_z,
                                    group="Drawers", role=NodeRole.DRAWER_FACE, metadata=meta, thickness=self.mat.mdf_thickness))
            for j, door in enumerate(r.doors):
                meta = DoorMetadata(
                    door_type=door.door_type.name,
                    hinge_side=door.hinge_side,
                    layer=door.layer,
                    cnc_enabled=self.cabinet.params.cnc_mode
                )
                self._add(SceneNode(PanelIdentity.make_door(self.cabinet_id, i, j),
                                    door.width, self.mat.mdf_thickness, door.height,
                                    door.x, door.y, door.z,
                                    group="Doors", role=NodeRole.DOOR_PANEL, metadata=meta, thickness=self.mat.mdf_thickness))
            if r.divider:
                self._add(SceneNode(PanelIdentity.make_divider(self.cabinet_id, i),
                                    r.divider.width, r.divider.depth, r.divider.height,
                                    r.divider.x, r.divider.y, r.divider.z,
                                    group="Dividers", role=NodeRole.DIVIDER, thickness=T))
        self.graph.validate_integrity()
        return self.graph

    def _build_from_construction_model(self, model: CabinetConstructionModel) -> SceneGraph:
        spec = model.specification
        thickness = spec.material_thickness_mm
        cabinet_depth = spec.depth_mm
        inner_width = spec.width_mm - (2 * thickness)
        back_thickness = spec.back_panel_thickness_mm
        shelf_z = spec.height_mm / 2.0

        for panel in model.panels:
            if panel.role == "SIDE_PANEL":
                side = "RIGHT" if "right" in panel.name.lower() else "LEFT"
                x_pos = 0.0 if side == "LEFT" else spec.width_mm - thickness
                self._add(
                    SceneNode(
                        PanelIdentity.make_side(self.cabinet_id, side),
                        panel.thickness_mm,
                        cabinet_depth,
                        panel.height_mm,
                        x_pos,
                        0.0,
                        0.0,
                        group="Carcass",
                        role=NodeRole.SIDE_PANEL,
                        thickness=panel.thickness_mm,
                        material=panel.material,
                    )
                )
            elif panel.role == "TOP_PANEL":
                self._add(
                    SceneNode(
                        PanelIdentity(self.cabinet_id, "SEC-TOP", SemanticRole.TOP),
                        inner_width,
                        cabinet_depth,
                        panel.thickness_mm,
                        thickness,
                        0.0,
                        spec.height_mm - thickness,
                        group="Carcass",
                        role=NodeRole.TOP_PANEL,
                        thickness=panel.thickness_mm,
                        material=panel.material,
                    )
                )
            elif panel.role == "BOTTOM_PANEL":
                self._add(
                    SceneNode(
                        PanelIdentity(self.cabinet_id, "SEC-BOTTOM", SemanticRole.BOTTOM),
                        inner_width,
                        cabinet_depth,
                        panel.thickness_mm,
                        thickness,
                        0.0,
                        0.0,
                        group="Carcass",
                        role=NodeRole.BOTTOM_PANEL,
                        thickness=panel.thickness_mm,
                        material=panel.material,
                    )
                )

        back_meta = BackPanelMetadata(
            section_index=0,
            section_label="REFERENCE",
            is_section_back=True,
            groove_depth=model.back_panel.groove_depth_mm,
            back_offset=20.0,
            extends_into_groove=True,
            source_rule="ConstructionResolver",
        )
        self._add(
            SceneNode(
                PanelIdentity(self.cabinet_id, "BACK", SemanticRole.BACK, 1),
                inner_width,
                back_thickness,
                spec.height_mm - (2 * thickness),
                thickness,
                cabinet_depth - back_thickness,
                thickness,
                group="Carcass",
                role=NodeRole.BACK_PANEL,
                metadata=back_meta,
                thickness=back_thickness,
                material=model.back_panel.panel.material,
            )
        )

        for index, shelf in enumerate(model.shelves):
            shelf_z_position = shelf_z
            self._add(
                SceneNode(
                    PanelIdentity.make_shelf(self.cabinet_id, 0, index),
                    shelf.width_mm,
                    shelf.depth_mm,
                    shelf.thickness_mm,
                    thickness,
                    0.0,
                    shelf_z_position,
                    group="Shelves",
                    role=NodeRole.SHELF,
                    thickness=shelf.thickness_mm,
                    material="MDF_18",
                )
            )

        self.graph.validate_integrity()
        return self.graph

    def _build_from_engineering_model(self, model: BaseCabinetEngineeringModel) -> SceneGraph:
        self._add(
            SceneNode(
                PanelIdentity.make_side(self.cabinet_id, "LEFT"),
                model.left_side_panel.width_mm,
                model.left_side_panel.depth_mm,
                model.left_side_panel.height_mm,
                model.left_side_panel.position_mm[0],
                model.left_side_panel.position_mm[1],
                model.left_side_panel.position_mm[2],
                group="Carcass",
                role=NodeRole.SIDE_PANEL,
                thickness=model.left_side_panel.thickness_mm,
                material=model.left_side_panel.material,
            )
        )
        self._add(
            SceneNode(
                PanelIdentity.make_side(self.cabinet_id, "RIGHT"),
                model.right_side_panel.width_mm,
                model.right_side_panel.depth_mm,
                model.right_side_panel.height_mm,
                model.right_side_panel.position_mm[0],
                model.right_side_panel.position_mm[1],
                model.right_side_panel.position_mm[2],
                group="Carcass",
                role=NodeRole.SIDE_PANEL,
                thickness=model.right_side_panel.thickness_mm,
                material=model.right_side_panel.material,
            )
        )
        self._add(
            SceneNode(
                PanelIdentity(self.cabinet_id, "SEC-TOP", SemanticRole.TOP),
                model.top_panel.width_mm,
                model.top_panel.depth_mm,
                model.top_panel.height_mm,
                model.top_panel.position_mm[0],
                model.top_panel.position_mm[1],
                model.top_panel.position_mm[2],
                group="Carcass",
                role=NodeRole.TOP_PANEL,
                thickness=model.top_panel.thickness_mm,
                material=model.top_panel.material,
            )
        )
        self._add(
            SceneNode(
                PanelIdentity(self.cabinet_id, "SEC-BOTTOM", SemanticRole.BOTTOM),
                model.bottom_panel.width_mm,
                model.bottom_panel.depth_mm,
                model.bottom_panel.height_mm,
                model.bottom_panel.position_mm[0],
                model.bottom_panel.position_mm[1],
                model.bottom_panel.position_mm[2],
                group="Carcass",
                role=NodeRole.BOTTOM_PANEL,
                thickness=model.bottom_panel.thickness_mm,
                material=model.bottom_panel.material,
            )
        )
        self._add(
            SceneNode(
                PanelIdentity(self.cabinet_id, "BACK", SemanticRole.BACK, 1),
                model.back_panel.width_mm,
                model.back_panel.depth_mm,
                model.back_panel.height_mm,
                model.back_panel.position_mm[0],
                model.back_panel.position_mm[1],
                model.back_panel.position_mm[2],
                group="Carcass",
                role=NodeRole.BACK_PANEL,
                metadata=BackPanelMetadata(
                    section_index=0,
                    section_label="REFERENCE",
                    is_section_back=True,
                    groove_depth=model.back_panel.groove_depth_mm,
                    back_offset=model.back_panel.position_mm[1],
                    extends_into_groove=(
                        model.back_panel.installation_mode
                        == BackPanelInstallationMode.GROOVED
                    ),
                    source_rule=model.back_panel.source_rule,
                ),
                thickness=model.back_panel.thickness_mm,
                material=model.back_panel.material,
            )
        )
        for divider in getattr(model, "dividers", []) or []:
            self._add(
                SceneNode(
                    PanelIdentity.make_divider(self.cabinet_id, divider.section_index),
                    divider.width_mm,
                    divider.depth_mm,
                    divider.height_mm,
                    divider.position_mm[0],
                    divider.position_mm[1],
                    divider.position_mm[2],
                    group="Dividers",
                    role=NodeRole.DIVIDER,
                    thickness=divider.depth_mm,
                )
            )
        for shelf in getattr(model, "shelves", []) or []:
            self._add(
                SceneNode(
                    PanelIdentity.make_shelf(self.cabinet_id, shelf.section_index, 0),
                    shelf.width_mm,
                    shelf.depth_mm,
                    shelf.thickness_mm,
                    shelf.position_mm[0],
                    shelf.position_mm[1],
                    shelf.position_mm[2],
                    group="Shelves",
                    role=NodeRole.SHELF,
                    thickness=shelf.thickness_mm,
                    material="MDF_18",
                )
            )

        self.graph.validate_integrity()
        return self.graph

    def _add(self, node):

        if getattr(node, "edge_spec", None) is None:
            node.edge_spec = EdgeBandRegistry.get_edges(
                node.role
            )

        self.graph.add_node(node)
