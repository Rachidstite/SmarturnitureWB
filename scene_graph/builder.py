import uuid
from engine.geometry_engine import GeometryEngine
from core.material_manager import MaterialManager
from scene_graph.node import SceneNode
from scene_graph.scene_graph import SceneGraph
from shared.identity import PanelIdentity, SemanticRole
from shared.roles import NodeRole
from manufacturing.edge_spec import EdgeBandRegistry
from scene_graph.metadata import DoorMetadata, DrawerMetadata

class SceneGraphBuilder:
    def __init__(self, cabinet, mat: MaterialManager):
        self.cabinet = cabinet
        self.mat = mat
        self.graph = SceneGraph()
        self.cabinet_id = str(uuid.uuid4())[:8]  # ديناميكي

    def build(self, geo: GeometryEngine) -> SceneGraph:
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
        bp_w = inner_W + 2 * self.mat.groove_depth
        bp_h = H - base_H - (2 * T) + (2 * self.mat.groove_depth)
        self._add(SceneNode(PanelIdentity(self.cabinet_id, "SEC-BACK", SemanticRole.BACK),
                            bp_w, self.mat.back_thickness, bp_h,
                            T - self.mat.groove_depth, D - 20 - self.mat.back_thickness,
                            base_H + T - self.mat.groove_depth, group="Carcass", role=NodeRole.BACK_PANEL, thickness=self.mat.back_thickness))
        if base_H > 0:
            self._add(SceneNode(PanelIdentity(self.cabinet_id, "SEC-PLINTH", SemanticRole.PLINTH),
                                inner_W, T, base_H, T, 20, 0, group="Carcass", role=NodeRole.PLINTH, thickness=T))
            self._add(SceneNode(PanelIdentity(self.cabinet_id, "SEC-PLINTH", SemanticRole.PLINTH),
                                inner_W, T, base_H, T, D - 20 - self.mat.back_thickness - T, 0,
                                group="Carcass", role=NodeRole.PLINTH, thickness=T))

        # --- الأقسام ---
        for i, r in enumerate(geo.resolved_sections):
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
        return self.graph

    def _add(self, node):
        self.graph.add_node(node)
