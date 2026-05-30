class UpdatePolicy:
    """العقد الأساسي لسياسات التحديث"""
    @staticmethod
    def apply_update(fc_obj, node, renderer_cls):
        raise NotImplementedError

class ShapeReplacePolicy(UpdatePolicy):
    """
    السياسة الافتراضية: Geometry is Disposable
    تقوم بتحديث الـ Shape بالكامل + الموقع + المظهر.
    تمنع مشاكل الـ Constraints عن طريق استبدال الهندسة بنظافة.
    """
    @staticmethod
    def apply_update(fc_obj, node, renderer_cls):
        # 1. Update Geometry (Disposable Shape)
        new_shape = renderer_cls.build_shape(node)
        if new_shape:
            fc_obj.Shape = new_shape
            
        # 2. Update Transform
        ShapeReplacePolicy.update_transform(fc_obj, node)
        
        # 3. Update Visuals
        ShapeReplacePolicy.update_visuals(fc_obj, node)

    @staticmethod
    def update_transform(fc_obj, node):
        import FreeCAD as App
        transform = getattr(node, 'transform', None)
        if transform and len(transform) >= 6:
            # افتراض: (x, y, z, roll, pitch, yaw)
            pos = App.Vector(transform[0], transform[1], transform[2])
            rot = App.Rotation(transform[5], transform[4], transform[3])
            fc_obj.Placement = App.Placement(pos, rot)

    @staticmethod
    def update_visuals(fc_obj, node):
        # سيتم دمجها لاحقاً لربط الألوان بالمواد (Material ID)
        pass

class TransformOnlyPolicy(UpdatePolicy):
    """سياسة سريعة O(1) لتحديث الموقع فقط بدون مساس بالهندسة"""
    @staticmethod
    def apply_update(fc_obj, node, renderer_cls):
        ShapeReplacePolicy.update_transform(fc_obj, node)

class VisualOnlyPolicy(UpdatePolicy):
    """سياسة لتحديث اللون أو المظهر فقط"""
    @staticmethod
    def apply_update(fc_obj, node, renderer_cls):
        ShapeReplacePolicy.update_visuals(fc_obj, node)
