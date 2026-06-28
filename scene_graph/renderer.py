try:
    import FreeCAD as App, Part
except ImportError:  # pragma: no cover - test environment fallback
    App = None
    Part = None
from scene_graph.node import SceneNode
from shared.roles import NodeRole
from core.material_manager import MaterialManager

from core.logging_config import logger
class SceneRenderer:
    def __init__(self, doc, mat: MaterialManager, hw, groups: dict, cnc_engine=None, placements=None):
        self.doc = doc; self.mat = mat; self.hw = hw; self.groups = groups; self.cnc_engine = cnc_engine
        self.placements = list(placements or [])

    @staticmethod
    def build_manufacturing_overlays(markers):
        return list(markers or [])

    def render(self, node: SceneNode):
        # استخدام الـ Registry
        from scene_graph.registry import RendererRegistry
        RendererRegistry.render(node, self)

    def render_graph(self, scene_graph):
        nodes = scene_graph.all_nodes()

        print("[TOTAL NODES]", len(nodes))

        for node in nodes:
            print("[NODE]", node.role, node.identity.key)
            self.render(node)

    def _ensure_group(self, group_name):
        if group_name not in self.groups:
            self.groups[group_name] = self.doc.addObject("App::DocumentObjectGroup", group_name)

    def hinge_offsets_for(self, door_id):
        offsets = []
        for placement in self.placements:
            if getattr(placement, "hardware_intent", None) != "INTENT_HINGE":
                continue
            if (
                getattr(placement, "host_node_id", None) != door_id
                and getattr(placement, "target_node_id", None) != door_id
            ):
                continue
            anchor = getattr(placement, "anchor", None)
            if anchor is None:
                continue
            offsets.append(anchor.offset_y)
        return sorted(offsets)

    def _render_simple_panel(self, node: SceneNode):
        print("[RENDER PANEL]", node.role, node.identity.key)
        """رسم افتراضي لأي لوح."""
        self._ensure_group(node.group)
        name = node.identity.key
        obj = self.doc.addObject("Part::Feature", name)
        obj.Shape = Part.makeBox(node.width, node.depth, node.height)
        obj.Placement = App.Placement(App.Vector(node.x, node.y, node.z), App.Rotation())
        obj.ViewObject.ShapeColor = self._visual_color_for(node)
        try:
            if node.role == NodeRole.BACK_PANEL:
                obj.ViewObject.Transparency = 35
            elif node.role == NodeRole.DIVIDER:
                obj.ViewObject.Transparency = 15
        except Exception:
            pass
        obj.addProperty("App::PropertyString", "SmartUUID")
        obj.SmartUUID = name
        self.groups[node.group].addObject(obj)

    @staticmethod
    def _visual_color_for(node: SceneNode):
        role_name = getattr(getattr(node, "role", None), "name", str(getattr(node, "role", None)))
        if role_name == "SIDE_PANEL":
            return (0.68, 0.49, 0.31)
        if role_name == "TOP_PANEL":
            return (0.75, 0.57, 0.36)
        if role_name == "BOTTOM_PANEL":
            return (0.72, 0.54, 0.34)
        if role_name == "BACK_PANEL":
            return (0.84, 0.85, 0.87)
        if role_name == "SHELF":
            return (0.90, 0.81, 0.62)
        if role_name == "DIVIDER":
            return (0.74, 0.57, 0.37)
        if role_name == "DRAWER_FACE":
            return (0.76, 0.64, 0.46)
        if role_name == "DOOR_PANEL":
            return (0.58, 0.41, 0.25)
        colors = {
            "Shelves": (0.90, 0.81, 0.62),
            "Drawers": (0.76, 0.64, 0.46),
            "Doors": (0.58, 0.41, 0.25),
            "Dividers": (0.74, 0.57, 0.37),
            "Carcass": (0.68, 0.49, 0.31),
        }
        return colors.get(getattr(node, "group", None), (0.68, 0.49, 0.31))

# --- تسجيل الاستراتيجيات ---
from scene_graph.registry import RendererRegistry

def _drawer_strategy(node, renderer):
    from builders.drawer_builder import DrawerBuilder

    meta = node.metadata
    renderer._ensure_group(node.group)
    DrawerBuilder.build(
        renderer.doc, renderer.groups[node.group], node.identity.key,
        node.width, node.height,  # face_w, face_h
        node.x, node.y, node.z,
        meta.box_w, meta.box_h, meta.box_d,
        meta.box_x, meta.box_y, meta.box_z,
        renderer.mat, meta.bottom_thickness
    )

def _door_strategy(node, renderer):
    from builders.door_builder import DoorBuilder

    meta = node.metadata
    renderer._ensure_group(node.group)
    door_type_str = meta.door_type.replace("_", " ").title()
    cnc = renderer.cnc_engine if meta.cnc_enabled else None
    hw_b = renderer.hw
    DoorBuilder.build(
        renderer.doc, renderer.groups[node.group], node.identity.key,
        node.width, node.height,
        node.x, node.y, node.z,
        renderer.mat, door_type_str,
        cnc, hw_b, renderer.groups.get("Hardware"),
        meta.hinge_side,
        meta.layer,
        hinge_offsets=renderer.hinge_offsets_for(node.identity.key) or None
    )

def _shelf_strategy(node, renderer):
    renderer._render_simple_panel(node)

def _divider_strategy(node, renderer):
    renderer._render_simple_panel(node)

RendererRegistry.register(NodeRole.SHELF, _shelf_strategy)
RendererRegistry.register(NodeRole.DIVIDER, _divider_strategy)
RendererRegistry.register(NodeRole.DRAWER_FACE, _drawer_strategy)
RendererRegistry.register(NodeRole.DOOR_PANEL, _door_strategy)
# باقي الأدوار تستخدم _render_simple_panel افتراضياً
