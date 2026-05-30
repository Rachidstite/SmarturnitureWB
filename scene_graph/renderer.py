import FreeCAD as App, Part
from scene_graph.node import SceneNode
from shared.roles import NodeRole
from builders.door_builder import DoorBuilder
from builders.drawer_builder import DrawerBuilder
from builders.hardware_builder import HardwareBuilder
from core.material_manager import MaterialManager

class SceneRenderer:
    def __init__(self, doc, mat: MaterialManager, hw: HardwareBuilder, groups: dict, cnc_engine=None):
        self.doc = doc; self.mat = mat; self.hw = hw; self.groups = groups; self.cnc_engine = cnc_engine

    def render(self, node: SceneNode):
        # استخدام الـ Registry
        from scene_graph.registry import RendererRegistry
        RendererRegistry.render(node, self)

    def _ensure_group(self, group_name):
        if group_name not in self.groups:
            self.groups[group_name] = self.doc.addObject("App::DocumentObjectGroup", group_name)

    def _render_simple_panel(self, node: SceneNode):
        """رسم افتراضي لأي لوح."""
        self._ensure_group(node.group)
        name = node.identity.key
        obj = self.doc.addObject("Part::Feature", name)
        obj.Shape = Part.makeBox(node.width, node.depth, node.height)
        obj.Placement = App.Placement(App.Vector(node.x, node.y, node.z), App.Rotation())
        colors = {"Shelves": (0.85,0.75,0.60), "Drawers": (0.9,0.8,0.7), "Doors": (0.6,0.4,0.2),
                  "Dividers": (0.85,0.75,0.60), "Carcass": (0.85,0.75,0.60)}
        obj.ViewObject.ShapeColor = colors.get(node.group, (0.85,0.75,0.60))
        obj.addProperty("App::PropertyString", "SmartUUID")
        obj.SmartUUID = name
        self.groups[node.group].addObject(obj)

# --- تسجيل الاستراتيجيات ---
from scene_graph.registry import RendererRegistry

def _drawer_strategy(node, renderer):
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
    meta = node.metadata
    renderer._ensure_group(node.group)
    door_type_str = meta.door_type.replace("_", " ").title()
    cnc = renderer.cnc_engine if meta.cnc_enabled else None
    hw_b = renderer.hw if meta.cnc_enabled else None
    DoorBuilder.build(
        renderer.doc, renderer.groups[node.group], node.identity.key,
        node.width, node.height,
        node.x, node.y, node.z,
        renderer.mat, door_type_str,
        cnc, hw_b, renderer.groups.get("Hardware"),
        meta.layer
    )

RendererRegistry.register(NodeRole.DRAWER_FACE, _drawer_strategy)
RendererRegistry.register(NodeRole.DOOR_PANEL, _door_strategy)
# باقي الأدوار تستخدم _render_simple_panel افتراضياً
