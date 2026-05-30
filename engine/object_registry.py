import FreeCAD as App

class PersistentObjectRegistry:
    """
    يعزل الـ Domain Identity عن تقلبات محرك FreeCAD.
    يحفظ خريطة: Domain Identity -> FreeCAD Internal Name
    """
    def __init__(self):
        self._map = {}  # Dict[str, str]

    def register(self, identity: str, fc_object):
        """تسجيل كائن جديد"""
        if fc_object is not None:
            self._map[identity] = fc_object.Name

    def resolve(self, doc, identity: str):
        """إرجاع الكائن الحقيقي بسرعة O(1) وبأمان"""
        fc_name = self._map.get(identity)
        if fc_name:
            fc_obj = doc.getObject(fc_name)
            if fc_obj:
                return fc_obj
            else:
                # الكائن تم حذفه من قبل المستخدم أو المحرك
                self.purge(identity)
        return None

    def purge(self, identity: str):
        """إزالة المرجع"""
        if identity in self._map:
            del self._map[identity]
