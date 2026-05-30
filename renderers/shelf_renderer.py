import Part
from engine.base_renderer import BaseRenderer
from engine.policies import ShapeReplacePolicy

class ShelfRenderer(BaseRenderer):
    """
    تطبيق حقيقي لمصيّر (Renderer) الرفوف.
    مسؤول حصرياً عن توليد الـ Geometry الخاص بالرف.
    """
    update_policy = ShapeReplacePolicy

    @classmethod
    def build_shape(cls, node):
        # توليد الصندوق الأساسي (Disposable Geometry)
        width = getattr(node, 'width', 0)
        thickness = getattr(node, 'thickness', 0)
        height = getattr(node, 'height', 0)
        
        box = Part.makeBox(width, thickness, height)
        
        # ⚡ هنا سيتم مستقبلاً إضافة عمليات الخصم (Boolean Cuts) لثقوب الـ CNC
        # if hasattr(node, 'manufacturing_ops'):
        #     box = apply_drilling_operations(box, node.manufacturing_ops)
        
        return box
