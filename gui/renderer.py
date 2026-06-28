import FreeCAD as App
import Part
from FreeCAD import Placement, Rotation, Vector

from domain.core_types import NodeRole
from manufacturing.visible_geometry_plan import build_visible_geometry_plan

try:
    import FreeCADGui as Gui
except ImportError:  # pragma: no cover - test environment fallback
    Gui = None


class GeometryRenderer:
    @staticmethod
    def render(project, engineering_report=None):
        doc_name = "SmartCabinetPro_Preview"

        try:
            doc = App.getDocument(doc_name)
            for obj in list(doc.Objects):
                doc.removeObject(obj.Name)
        except NameError:
            doc = App.newDocument(doc_name)

        group = doc.addObject(
            "App::DocumentObjectGroup",
            project.uid if hasattr(project, "uid") else "Cabinet_Assembly",
        )

        cabinet_depth = getattr(getattr(project, "topology", None), "d", 600.0)
        physical_nodes = list(getattr(project.graph, "physical_nodes", []) or [])

        for node in physical_nodes:
            GeometryRenderer._render_cabinet_panel(doc, group, node, cabinet_depth)

        plan = build_visible_geometry_plan(project)
        GeometryRenderer._render_manufacturing_geometry(
            doc,
            group,
            plan.features,
        )

        if engineering_report is not None:
            setattr(project, "engineering_report", engineering_report)

        doc.recompute()

        if App.GuiUp and Gui is not None:
            try:
                Gui.ActiveDocument.ActiveView.fitAll()
            except Exception:
                pass

        return doc

    @staticmethod
    def _render_cabinet_panel(doc, group, node, cabinet_depth):
        dx, dy, dz = GeometryRenderer._get_dimensions(node)
        box_shape = Part.makeBox(dx, dy, dz)

        safe_name = node.identity.key.replace("-", "_").replace(".", "_")
        obj = doc.addObject("Part::Feature", safe_name)
        obj.Shape = box_shape

        transform = getattr(node, "transform", None)
        actual_y = cabinet_depth - getattr(transform, "y", 0.0) - dy
        obj.Placement = Placement(
            Vector(
                getattr(transform, "x", 0.0),
                actual_y,
                getattr(transform, "z", 0.0),
            ),
            Rotation(
                getattr(transform, "rot_x", 0.0),
                getattr(transform, "rot_y", 0.0),
                getattr(transform, "rot_z", 0.0),
            ),
        )
        obj.Label = f"{getattr(node.role, 'name', 'UNKNOWN')} [{node.identity.key}]"

        if App.GuiUp and Gui is not None:
            try:
                obj.ViewObject.ShapeColor = GeometryRenderer._get_color(node.role)
            except Exception:
                pass

        group.addObject(obj)

    @staticmethod
    def _render_manufacturing_geometry(doc, group, features):
        manufacturing_group = doc.addObject(
            "App::DocumentObjectGroup",
            "Manufacturing_Geometry",
        )
        group.addObject(manufacturing_group)

        for feature in features:
            GeometryRenderer._render_feature(doc, manufacturing_group, feature)

    @staticmethod
    def _render_feature(doc, group, feature):
        shape = GeometryRenderer._make_feature_shape(feature)
        if shape is None:
            return

        obj = doc.addObject("Part::Feature", feature.name)
        obj.Shape = shape

        rotation = GeometryRenderer._feature_rotation(feature)
        obj.Placement = Placement(Vector(*feature.placement), rotation)
        obj.Label = feature.label or feature.name

        if App.GuiUp and Gui is not None:
            try:
                obj.ViewObject.ShapeColor = feature.color
            except Exception:
                pass
            try:
                obj.ViewObject.Transparency = 35 if feature.prototype else 10
            except Exception:
                pass

        group.addObject(obj)

    @staticmethod
    def _make_feature_shape(feature):
        kind = str(getattr(feature, "kind", "") or "").lower()
        size = getattr(feature, "size", (0.0, 0.0, 0.0))
        sx, sy, sz = (float(size[0]), float(size[1]), float(size[2]))

        if kind in {"back_panel_groove", "drawer_slide_line", "wall_mount_prototype"}:
            return Part.makeBox(max(sx, 0.1), max(sy, 0.1), max(sz, 0.1))

        if kind in {"hinge_plate_position"}:
            return Part.makeBox(max(sx, 0.1), max(sy, 0.1), max(sz, 0.1))

        if kind in {"hinge_cup_hole", "shelf_pin_hole", "drilling_indicator"}:
            radius = max(sx / 2.0, 0.5)
            height = max(sy, 0.1)
            return Part.makeCylinder(radius, height)

        return Part.makeBox(max(sx, 0.1), max(sy, 0.1), max(sz, 0.1))

    @staticmethod
    def _feature_rotation(feature):
        kind = str(getattr(feature, "kind", "") or "").lower()
        if kind == "hinge_cup_hole":
            return Rotation(Vector(1, 0, 0), 90)
        if kind in {"shelf_pin_hole", "drilling_indicator"}:
            return Rotation(Vector(0, 1, 0), 90)
        return Rotation()

    @staticmethod
    def _get_dimensions(node) -> tuple:
        role = node.role
        w, h, t = node.width, node.height, node.thickness

        if role in [NodeRole.SIDE_PANEL, NodeRole.DIVIDER]:
            return (t, w, h)
        if role in [NodeRole.TOP_PANEL, NodeRole.BOTTOM_PANEL, NodeRole.SHELF]:
            return (w, h, t)
        if role in [NodeRole.BACK_PANEL, NodeRole.DOOR_PANEL]:
            return (w, t, h)
        return (w, h, t)

    @staticmethod
    def _get_color(role) -> tuple:
        role_name = getattr(role, "name", str(role))
        if role_name == "SIDE_PANEL":
            return (0.68, 0.49, 0.31)
        if role_name == "TOP_PANEL":
            return (0.75, 0.57, 0.36)
        if role_name == "BOTTOM_PANEL":
            return (0.72, 0.54, 0.34)
        if role_name == "BACK_PANEL":
            return (0.84, 0.85, 0.87)
        if role_name == "DOOR_PANEL":
            return (0.58, 0.41, 0.25)
        if role_name == "SHELF":
            return (0.90, 0.81, 0.62)
        if role_name == "DIVIDER":
            return (0.74, 0.57, 0.37)
        if role_name == "DRAWER_FACE":
            return (0.76, 0.64, 0.46)
        if role_name == "PLINTH":
            return (0.36, 0.36, 0.36)
        return (0.68, 0.49, 0.31)
