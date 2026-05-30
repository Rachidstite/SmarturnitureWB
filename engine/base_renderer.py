from engine.policies import ShapeReplacePolicy

class BaseRenderer:
    """
    الطبقة المجردة لكل المصيِّرات (Renderers).
    تفصل بين سياسة التحديث (Policy) ومنطق بناء الشكل (Build Logic).
    """
    
    # السياسة الافتراضية هي الاستبدال الكامل الذكي
    update_policy = ShapeReplacePolicy

    @classmethod
    def create_new(cls, doc, node):
        """إنشاء كائن جديد (Stateless Feature)"""
        uid = node.identity.key if hasattr(node.identity, 'key') else str(node.identity)
        
        # نستخدم Part::Feature خفيف الوزن بدلاً من كائنات معقدة تسبب مشاكل Constraints
        fc_obj = doc.addObject("Part::Feature", uid)
        fc_obj.Label = uid
        
        # نستخدم السياسة لتطبيق البيانات على الكائن الفارغ
        cls.update_policy.apply_update(fc_obj, node, cls)
        return fc_obj

    @classmethod
    def update_existing(cls, fc_obj, node):
        """تحديث كائن موجود مسبقاً بناءً على سياسته"""
        cls.update_policy.apply_update(fc_obj, node, cls)

    @classmethod
    def build_shape(cls, node):
        """
        يجب على كل Renderer وراثة هذه الدالة لبناء الـ TopoShape الخاص به.
        المحرك لا يرسم، المحرك يعيد فقط FreeCAD.Part.Shape خالص.
        """
        raise NotImplementedError("Renderer must implement build_shape")
