import FreeCAD as App, Part, FreeCADGui as Gui
from dataclasses import replace
from types import SimpleNamespace
from core.material_manager import MaterialManager
from core.logging_config import logger
from cnc.cnc_builder import CNCBuilder
from builders.door_builder import DoorBuilder
from builders.drawer_builder import DrawerBuilder
from builders.hardware_builder import HardwareBuilder
from services.project_service import ProjectService
from engine.cabinet import Cabinet
from engine.geometry_engine import GeometryEngine
from scene_graph.builder import SceneGraphBuilder
from scene_graph.renderer import SceneRenderer
from assembly.assembly_graph_builder import AssemblyGraphBuilder
from domain.system32 import System32Engine
from manufacturing.visible_geometry_plan import build_visible_geometry_plan
from domain.base_cabinet_engineering_model import (
    EngineeringDoorPlacement,
    EngineeringDividerPlacement,
    EngineeringShelfPlacement,
)

class CabinetBuilder:
    def __init__(self):
        self.mat = MaterialManager(); self.cnc = CNCBuilder(self.mat); self.hw = None
        self.groups = {}; self.drilling_z_positions = []; self._cabinet = None
        self._doc = None
        self.geo = None
        self.scene_graph = None
        self.assembly_graph = None

    def build(self, cabinet: Cabinet):
        logger.debug("BUILD STARTED")
        self._cabinet = cabinet
        if hasattr(cabinet.params, 'back_thickness'): self.mat.back_thickness = cabinet.params.back_thickness
        if hasattr(cabinet.params, 'drawer_depth'): self.mat.drawer_depth = cabinet.params.drawer_depth
        if hasattr(cabinet.params, 'drawer_bottom_thickness'): self.mat.drawer_bottom_thickness = cabinet.params.drawer_bottom_thickness

        doc = ProjectService.get_or_create_document()
        self._doc = doc
        self.hw = HardwareBuilder(doc)
        self._setup_groups(doc)
        ProjectService.clear_all_panels(doc)

        self.geo = GeometryEngine(cabinet, self.mat)
        self.geo.resolve_all()
        self._attach_section_engineering_components()

        sg_builder = SceneGraphBuilder(cabinet, self.mat)
        self.scene_graph = sg_builder.build(self.geo)

        self.assembly_graph = AssemblyGraphBuilder.build(
            self.scene_graph
        )

        print(
            "[ASSEMBLY JOINTS]",
            len(self.assembly_graph.all_joints())
        )

        print(
            "[ASSEMBLY JOINTS]",
            len(self.assembly_graph.all_joints())
        )
        logger.debug(f"BUILDABLE: {self.geo.is_buildable}, Sections: {len(self.geo.resolved_sections)}")
        if not self.geo.is_buildable:
            logger.error("Build aborted: unbuildable.")
            return

        doc.openTransaction("Build Cabinet")
        try:
            self._build_geometry(doc, cabinet)
            doc.commitTransaction()
        except Exception as e:
            doc.abortTransaction(); logger.error(f"Build failed: {e}"); raise
        doc.recompute()
        logger.debug(f"OBJECT COUNT: {len(doc.Objects)}")
        Gui.activeDocument().activeView().viewAxometric()
        Gui.SendMsgToActiveView("ViewFit")

    def _setup_groups(self, doc):
        for g_name in ["Carcass", "Dividers", "Shelves", "Drawers", "Doors", "Hardware"]:
            obj = doc.getObject(g_name)
            if obj: self.groups[g_name] = obj
            else: self.groups[g_name] = doc.addObject("App::DocumentObjectGroup", g_name)

    def _attach_section_engineering_components(self):
        # Transitional bridge: section layout still comes from GeometryEngine.
        # The long-term contract remains ConstructionModel -> EngineeringModel.
        engineering_model = getattr(self._cabinet, "engineering_model", None)
        if engineering_model is None:
            return

        thickness = self.mat.mdf_thickness
        shelf_thickness = thickness
        shelves = []
        dividers = []
        doors = []

        for index, section in enumerate(getattr(self.geo, "resolved_sections", []) or []):
            section_id = f"SEC-{index + 1}"
            for shelf_index, shelf in enumerate(getattr(section, "shelves", []) or []):
                shelves.append(
                    EngineeringShelfPlacement(
                        name=f"{section_id}_Shelf_{shelf_index + 1}",
                        section_index=index,
                        section_id=section_id,
                        source_rule="GeometryEngineResolvedSection:TRANSITIONAL_BRIDGE",
                        width_mm=shelf.width,
                        depth_mm=shelf.depth,
                        thickness_mm=shelf_thickness,
                        position_mm=(shelf.x, shelf.y, shelf.z),
                    )
                )
            for door_index, door in enumerate(getattr(section, "doors", []) or []):
                doors.append(
                    EngineeringDoorPlacement(
                        name=f"{section_id}_Door_{door_index + 1}",
                        section_index=index,
                        section_id=section_id,
                        door_index=door_index,
                        source_rule="resolved_door_projection",
                        x_mm=door.x,
                        y_mm=door.y,
                        z_mm=door.z,
                        width_mm=door.width,
                        height_mm=door.height,
                        thickness_mm=thickness,
                        door_type=door.door_type,
                        hinge_side=door.hinge_side,
                        layer=door.layer,
                        material=getattr(
                            getattr(engineering_model, "left_side_panel", None),
                            "material",
                            "",
                        ),
                    )
                )
            divider = getattr(section, "divider", None)
            if divider is not None:
                dividers.append(
                    EngineeringDividerPlacement(
                        name=f"{section_id}_Divider",
                        section_index=index,
                        section_id=section_id,
                        source_rule="GeometryEngineResolvedSection:TRANSITIONAL_BRIDGE",
                        width_mm=divider.width,
                        depth_mm=divider.depth,
                        height_mm=divider.height,
                        position_mm=(divider.x, divider.y, divider.z),
                    )
                )

        self._cabinet.engineering_model = replace(
            engineering_model,
            doors=tuple(doors),
            shelves=tuple(shelves),
            dividers=tuple(dividers),
        )

    def _build_geometry(self, doc, cabinet: Cabinet):
        self._cabinet = cabinet; self._doc = doc; self.drilling_z_positions = []
        for i, sec in enumerate(cabinet.sections):
            r = self.geo.resolved_sections[i]
        visible_geometry_source = SimpleNamespace(
            graph=self.scene_graph,
            topology=SimpleNamespace(d=self._cabinet.params.depth),
        )
        visible_geometry_plan = build_visible_geometry_plan(visible_geometry_source)
        renderer = SceneRenderer(
            self._doc,
            self.mat,
            self.hw,
            self.groups,
            self.cnc if self._cabinet.params.cnc_mode else None,
            panel_features=visible_geometry_plan.features,
        )

        print("[SCENE GRAPH] rendering all nodes")
        renderer.render_graph(self.scene_graph)

        if self._cabinet.params.hw_mode: self._add_carcass_joinery()

    
    def _render_shelves(self, sec_idx, r):
        from shared.roles import NodeRole

        renderer = SceneRenderer(
            self._doc,
            self.mat,
            self.hw,
            self.groups
        )

        section_id = f"SEC-{sec_idx+1}"

        for node in self.scene_graph.all_nodes():
            print("[NODE]", node.role, getattr(node.identity, "section_id", "NO_SECTION"), node.identity.key)
            if (
                node.role == NodeRole.SHELF
                and getattr(node.identity, "section_id", "") == section_id
            ):
                print("[RENDER SHELF]", node.identity.key)
                renderer.render(node)

    

    def _build_carcass(self):
        p = self._cabinet.params; T, D, H = self.mat.mdf_thickness, p.depth, p.height
        W, base_H, bp_offset = p.width, p.base_height, 20
        G, BT = self.mat.groove_depth, self.mat.back_thickness
        inner_W = W - 2 * T

        side_l = Part.makeBox(T, D, H - T); side_r = Part.makeBox(T, D, H - T)
        if p.cnc_mode:
            side_l = self.cnc.generate_side_screw_holes(side_l, self.drilling_z_positions, D, self._sliding_space(), True)
            side_r = self.cnc.generate_side_screw_holes(side_r, self.drilling_z_positions, D, self._sliding_space(), False)
            groove_z_start = base_H + T
            groove_h = (H - T) - groove_z_start
            grv_l = Part.makeBox(G, BT, groove_h)
            grv_l.Placement = App.Placement(App.Vector(T - G, D - bp_offset - BT, groove_z_start), App.Rotation())
            side_l = side_l.cut(grv_l)
            grv_r = Part.makeBox(G, BT, groove_h)
            grv_r.Placement = App.Placement(App.Vector(0, D - bp_offset - BT, groove_z_start), App.Rotation())
            side_r = side_r.cut(grv_r)

        self._create_panel(self._doc, "Side_Left", T, D, H - T, (0, 0, 0), "Carcass", custom_shape=side_l)
        self._create_panel(self._doc, "Side_Right", T, D, H - T, (W - T, 0, 0), "Carcass", custom_shape=side_r)

        bot_shape = Part.makeBox(inner_W, D, T)
        top_shape = Part.makeBox(self.geo.resolved_top.width, self.geo.resolved_top.depth,
                                 self.geo.resolved_top.thickness)
        if p.cnc_mode:
            grv_b = Part.makeBox(inner_W, BT, G)
            grv_b.Placement = App.Placement(App.Vector(0, D - bp_offset - BT, T - G), App.Rotation())
            bot_shape = bot_shape.cut(grv_b)

        self._create_panel(self._doc, "Bottom", inner_W, D, T, (T, 0, base_H), "Carcass", custom_shape=bot_shape)
        self._create_panel(self._doc, "Top", self.geo.resolved_top.width, self.geo.resolved_top.depth,
                           self.geo.resolved_top.thickness,
                           (self.geo.resolved_top.x, self.geo.resolved_top.y, self.geo.resolved_top.z), "Carcass",
                           custom_shape=top_shape)

    
    def _build_back_panel(self):
        back_nodes = [
            node for node in self.scene_graph.all_nodes()
            if getattr(getattr(node, "role", None), "name", "") == "BACK_PANEL"
        ]
        back_nodes.sort(key=lambda node: getattr(getattr(node, "metadata", None), "section_index", 0))

        for index, node in enumerate(back_nodes):
            metadata = getattr(node, "metadata", None)
            section_index = getattr(metadata, "section_index", index)
            self._create_panel(
                self._doc,
                f"Back_Section_{section_index + 1}",
                node.width,
                node.depth,
                node.height,
                (node.x, node.y, node.z),
                node.group,
                color=(0.9, 0.9, 0.9)
            )



    def _build_base(self):
        p = self._cabinet.params; T = self.mat.mdf_thickness; bp_offset = 20; BT = self.mat.back_thickness
        inner_W = p.width - 2 * T
        if p.base_height > 0:
            self._create_panel(self._doc, "Plinth_Front", inner_W, T, p.base_height, (T, 20, 0), "Carcass",
                               (0.3, 0.3, 0.3))
            self._create_panel(self._doc, "Plinth_Back", inner_W, T, p.base_height,
                               (T, p.depth - bp_offset - BT - T, 0), "Carcass", (0.3, 0.3, 0.3))

    def _add_carcass_joinery(self):
        p = self._cabinet.params; T = self.mat.mdf_thickness; D, H, W = p.depth, p.height, p.width
        base_H, bp_offset = p.base_height, 20; BT = self.mat.back_thickness; slide = self._sliding_space()
        front_offset = 64.0; back_offset = 64.0
        y_front = slide + front_offset; y_back = D - bp_offset - BT - back_offset

        self.hw.add_minifix("Mfx_Left_Bot_F", (T, y_front, base_H + T / 2), self.groups["Hardware"])
        self.hw.add_minifix("Mfx_Left_Bot_B", (T, y_back, base_H + T / 2), self.groups["Hardware"])
        self.hw.add_minifix("Mfx_Left_Top_F", (T, y_front, H - T / 2), self.groups["Hardware"])
        self.hw.add_minifix("Mfx_Left_Top_B", (T, y_back, H - T / 2), self.groups["Hardware"])

        self.hw.add_minifix("Mfx_Right_Bot_F", (W - T, y_front, base_H + T / 2), self.groups["Hardware"])
        self.hw.add_minifix("Mfx_Right_Bot_B", (W - T, y_back, base_H + T / 2), self.groups["Hardware"])
        self.hw.add_minifix("Mfx_Right_Top_F", (W - T, y_front, H - T / 2), self.groups["Hardware"])
        self.hw.add_minifix("Mfx_Right_Top_B", (W - T, y_back, H - T / 2), self.groups["Hardware"])

        sec_count = p.sec_count
        if sec_count > 1:
            inner_W = W - 2 * T; sec_W = (inner_W - (T * (sec_count - 1))) / sec_count
            for i in range(1, sec_count):
                div_x = T + i * (sec_W + T)
                self.hw.add_minifix(f"Mfx_Div{i}_Bot_F", (div_x, y_front, base_H + T / 2), self.groups["Hardware"])
                self.hw.add_minifix(f"Mfx_Div{i}_Bot_B", (div_x, y_back, base_H + T / 2), self.groups["Hardware"])
                self.hw.add_minifix(f"Mfx_Div{i}_Top_F", (div_x, y_front, H - T / 2), self.groups["Hardware"])
                self.hw.add_minifix(f"Mfx_Div{i}_Top_B", (div_x, y_back, H - T / 2), self.groups["Hardware"])

    def _sliding_space(self):
        return self.mat.sliding_track_depth if any(
            "Sliding" in sec.config.doors for sec in self._cabinet.sections) else 0

    def _create_panel(self, doc, name, w, d, h, pos, group_name, color=(0.85, 0.75, 0.60), custom_shape=None):
        if group_name not in self.groups:
            self.groups[group_name] = self._doc.addObject("App::DocumentObjectGroup", group_name)
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = custom_shape if custom_shape else Part.makeBox(w, d, h)
        obj.Placement = App.Placement(App.Vector(*pos), App.Rotation())
        obj.ViewObject.ShapeColor = color
        obj.addProperty("App::PropertyString", "SmartFurniture_Role")
        obj.SmartFurniture_Role = group_name
        self.groups[group_name].addObject(obj)
        return obj
