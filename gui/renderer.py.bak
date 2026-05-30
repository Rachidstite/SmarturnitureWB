import FreeCAD as App
import Part
from FreeCAD import Placement, Vector, Rotation
from domain.core_types import NodeRole

try:
    import FreeCADGui as Gui
except ImportError:
    Gui = None

class GeometryRenderer:
    @staticmethod
    def render(project):
        doc_name = "SmartCabinetPro_Preview"
        
        try:
            doc = App.getDocument(doc_name)
            for obj in doc.Objects:
                doc.removeObject(obj.Name)
        except NameError:
            doc = App.newDocument(doc_name)

        group = doc.addObject("App::DocumentObjectGroup", project.uid if hasattr(project, 'uid') else "Cabinet_Assembly")

        # جلب العمق الكلي للخزانة ديناميكياً لعمل عملية المرآة البصرية
        cabinet_depth = getattr(getattr(project, 'topology', None), 'd', 600.0)

        for node in getattr(project.graph, 'physical_nodes', []):
            dx, dy, dz = GeometryRenderer._get_dimensions(node)
            box_shape = Part.makeBox(dx, dy, dz)
            
            safe_name = node.identity.key.replace("-", "_").replace(".", "_")
            obj = doc.addObject("Part::Feature", safe_name)
            obj.Shape = box_shape
            
            t = node.transform
            
            # ⚡ الـقـالـب الـمـعـمـاري الـحـاسـم:
            # نقوم بطرح إحداثي Y وعمقه من العمق الكلي للخزانة لقلب المنظور بصرياً فقط 
            # ليصبح الأمام أماماً والخلف خلفاً في شاشة العرض دون المساس ببيانات الإنتاج
            actual_y = cabinet_depth - t.y - dy
            
            obj.Placement = Placement(Vector(t.x, actual_y, t.z), Rotation(t.rot_x, t.rot_y, t.rot_z))
            obj.Label = f"{node.role.name} [{node.identity.key}]"
            
            if App.GuiUp and Gui is not None:
                try:
                    obj.ViewObject.ShapeColor = GeometryRenderer._get_color(node.role)
                except Exception:
                    pass
            
            group.addObject(obj)

        doc.recompute()
        
        if App.GuiUp and Gui is not None:
            try:
                Gui.ActiveDocument.ActiveView.fitAll()
            except Exception:
                pass
                
        return doc

    @staticmethod
    def _get_dimensions(node) -> tuple:
        role = node.role
        w, h, t = node.width, node.height, node.thickness
        
        if role in [NodeRole.SIDE_PANEL, NodeRole.DIVIDER]:
            return (t, w, h)
        elif role in [NodeRole.TOP_PANEL, NodeRole.BOTTOM_PANEL, NodeRole.SHELF]:
            return (w, h, t)
        elif role in [NodeRole.BACK_PANEL, NodeRole.DOOR_PANEL]:
            return (w, t, h)
        else:
            return (w, h, t)

    @staticmethod
    def _get_color(role) -> tuple:
        if role == NodeRole.BACK_PANEL: return (0.8, 0.8, 0.8)   
        if role == NodeRole.DOOR_PANEL: return (0.6, 0.8, 0.9)   
        if role == NodeRole.SHELF: return (0.9, 0.8, 0.6)        
        return (0.7, 0.5, 0.3)                                   
