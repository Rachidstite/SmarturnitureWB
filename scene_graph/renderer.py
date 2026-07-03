try:
    import FreeCAD as App, Part
except ImportError:  # pragma: no cover - test environment fallback
    App = None
    Part = None
from scene_graph.node import SceneNode
from shared.roles import NodeRole
from core.material_manager import MaterialManager
from manufacturing.panel_shape_processor import process_panel_shape
from scene_graph.metadata import EngineeringDrawerFaceMetadata, build_visual_metadata
class SceneRenderer:
    def __init__(self, doc, mat: MaterialManager, hw, groups: dict, cnc_engine=None, placements=None, panel_features=None):
        self.doc = doc; self.mat = mat; self.hw = hw; self.groups = groups; self.cnc_engine = cnc_engine
        self.placements = list(placements or [])
        self.panel_features = list(panel_features or [])

    @staticmethod
    def build_manufacturing_overlays(markers):
        return list(markers or [])

    @staticmethod
    def build_visual_overlays(visual_metadata):
        if visual_metadata is None:
            return []

        overlays = []
        overlays.extend(
            SceneRenderer._edge_band_overlays(
                getattr(visual_metadata, "edge_banding", ()) or ()
            )
        )
        overlays.extend(
            SceneRenderer._drill_hole_overlays(
                getattr(visual_metadata, "drill_holes", ()) or ()
            )
        )
        overlays.extend(
            SceneRenderer._groove_overlays(
                getattr(visual_metadata, "grooves", ()) or ()
            )
        )
        overlays.extend(
            SceneRenderer._hardware_marker_overlays(
                getattr(visual_metadata, "hardware_markers", ()) or ()
            )
        )
        return overlays

    @staticmethod
    def build_viewport_overlay_commands(overlays):
        commands = []
        for overlay in overlays or []:
            overlay_type = str(overlay.get("overlay_type", "") or "")
            if overlay_type == "edge_banding":
                command = SceneRenderer._edge_viewport_command(overlay)
            elif overlay_type == "drill_hole":
                command = SceneRenderer._drill_viewport_command(overlay)
            elif overlay_type == "groove":
                command = SceneRenderer._groove_viewport_command(overlay)
            elif overlay_type == "hardware_marker":
                command = SceneRenderer._hardware_viewport_command(overlay)
            else:
                continue
            if command is not None:
                commands.append(command)
        return commands

    @staticmethod
    def resolve_visual_metadata(
        node,
        *,
        cnc_report=None,
        hardware_bom=None,
        assembly_report=None,
    ):
        return build_visual_metadata(
            node,
            cnc_report=cnc_report,
            hardware_bom=hardware_bom,
            assembly_report=assembly_report,
        )

    @staticmethod
    def _edge_band_overlays(edge_banding):
        return [
            {
                "overlay_type": "edge_banding",
                "visual_type": "EDGE_MARKER",
                "side": str(getattr(item, "side", "") or ""),
                "banding": str(getattr(item, "banding", "") or ""),
                "label": str(getattr(item, "label", "") or ""),
            }
            for item in edge_banding
        ]

    @staticmethod
    def _drill_hole_overlays(drill_holes):
        return [
            {
                "overlay_type": "drill_hole",
                "visual_type": "CIRCLE",
                "panel_identity": str(getattr(item, "panel_identity", "") or ""),
                "face": str(getattr(item, "face", "") or ""),
                "x": float(getattr(item, "x", 0.0) or 0.0),
                "y": float(getattr(item, "y", 0.0) or 0.0),
                "z": float(getattr(item, "z", 0.0) or 0.0),
                "diameter": float(getattr(item, "diameter", 0.0) or 0.0),
                "depth": float(getattr(item, "depth", 0.0) or 0.0),
                "axis": str(getattr(item, "axis", "Z") or "Z"),
                "is_through": bool(getattr(item, "is_through", False)),
                "source_operation_reference": str(
                    getattr(item, "source_operation_reference", "") or ""
                ),
            }
            for item in drill_holes
        ]

    @staticmethod
    def _groove_overlays(grooves):
        return [
            {
                "overlay_type": "groove",
                "visual_type": "CENTERLINE",
                "panel_identity": str(getattr(item, "panel_identity", "") or ""),
                "face": str(getattr(item, "face", "") or ""),
                "depth": float(getattr(item, "depth", 0.0) or 0.0),
                "label": str(getattr(item, "label", "") or ""),
                "source_rule": str(getattr(item, "source_rule", "") or ""),
            }
            for item in grooves
        ]

    @staticmethod
    def _hardware_marker_overlays(hardware_markers):
        return [
            {
                "overlay_type": "hardware_marker",
                "visual_type": SceneRenderer._hardware_visual_type(item),
                "panel_identity": str(getattr(item, "panel_identity", "") or ""),
                "sku": str(getattr(item, "sku", "") or ""),
                "quantity": int(getattr(item, "quantity", 0) or 0),
                "hardware_category": str(getattr(item, "hardware_category", "") or ""),
                "label": str(getattr(item, "label", "") or ""),
                "component_reference": tuple(
                    getattr(item, "component_reference", ()) or ()
                ),
                "cabinet_reference": tuple(
                    getattr(item, "cabinet_reference", ()) or ()
                ),
                "source_operation_references": tuple(
                    getattr(item, "source_operation_references", ()) or ()
                ),
            }
            for item in hardware_markers
        ]

    @staticmethod
    def _hardware_visual_type(item):
        category = str(getattr(item, "hardware_category", "") or "").upper()
        sku = str(getattr(item, "sku", "") or "").upper()
        text = " ".join(
            (
                category,
                sku,
                str(getattr(item, "label", "") or "").upper(),
            )
        )
        if "HINGE" in text:
            return "HINGE_SYMBOL"
        if "DRAWER_SLIDE" in text or "SLIDE" in text:
            return "DRAWER_SLIDE_SYMBOL"
        if "SHELF_PIN" in text or "SHELF PIN" in text:
            return "SHELF_PIN_SYMBOL"
        return "HARDWARE_SYMBOL"

    @staticmethod
    def _edge_viewport_command(overlay):
        return {
            "command_type": "edge_marker",
            "overlay_type": "edge_banding",
            "label": str(overlay.get("label", "") or ""),
            "side": str(overlay.get("side", "") or ""),
            "banding": str(overlay.get("banding", "") or ""),
            "position": None,
            "face": "",
            "source_reference": "",
        }

    @staticmethod
    def _drill_viewport_command(overlay):
        return {
            "command_type": "circle_marker",
            "overlay_type": "drill_hole",
            "label": str(overlay.get("label", "") or "Drill hole"),
            "position": (
                float(overlay.get("x", 0.0) or 0.0),
                float(overlay.get("y", 0.0) or 0.0),
                float(overlay.get("z", 0.0) or 0.0),
            ),
            "face": str(overlay.get("face", "") or ""),
            "diameter": float(overlay.get("diameter", 0.0) or 0.0),
            "size": float(overlay.get("diameter", 0.0) or 0.0),
            "source_reference": str(overlay.get("source_operation_reference", "") or ""),
            "panel_identity": str(overlay.get("panel_identity", "") or ""),
        }

    @staticmethod
    def _groove_viewport_command(overlay):
        face = str(overlay.get("face", "") or "")
        source_rule = str(overlay.get("source_rule", "") or "")
        if not face and not source_rule:
            return None
        return {
            "command_type": "centerline_marker",
            "overlay_type": "groove",
            "label": str(overlay.get("label", "") or ""),
            "position": None,
            "face": face,
            "depth": float(overlay.get("depth", 0.0) or 0.0),
            "size": float(overlay.get("depth", 0.0) or 0.0),
            "source_reference": source_rule,
            "panel_identity": str(overlay.get("panel_identity", "") or ""),
        }

    @staticmethod
    def _hardware_viewport_command(overlay):
        return {
            "command_type": "symbolic_marker",
            "overlay_type": "hardware_marker",
            "label": str(overlay.get("label", "") or overlay.get("sku", "") or ""),
            "symbol": str(overlay.get("visual_type", "") or "HARDWARE_SYMBOL"),
            "position": None,
            "face": "",
            "size": int(overlay.get("quantity", 0) or 0),
            "source_reference": tuple(
                overlay.get("source_operation_references", ()) or ()
            ),
            "panel_identity": str(overlay.get("panel_identity", "") or ""),
            "sku": str(overlay.get("sku", "") or ""),
        }

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
        base_shape = Part.makeBox(node.width, node.depth, node.height)
        if node.role in (NodeRole.BACK_PANEL, NodeRole.SIDE_PANEL, NodeRole.DIVIDER):
            obj.Shape = process_panel_shape(
                base_shape,
                node,
                self.panel_features,
                panel_origin=(node.x, node.y, node.z),
            )
        else:
            obj.Shape = base_shape
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
    meta = node.metadata
    renderer._ensure_group(node.group)
    if isinstance(meta, EngineeringDrawerFaceMetadata) or getattr(
        meta,
        "source_rule",
        "",
    ) == "resolved_drawer_face_projection":
        renderer._render_simple_panel(node)
        return

    from builders.drawer_builder import DrawerBuilder

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
