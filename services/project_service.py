import FreeCAD as App
from core.logging_config import logger
class ProjectService:
    DOC_NAME = "Pro_Dressing_CNC"
    @classmethod
    def get_or_create_document(cls):
        doc = App.ActiveDocument
        if not doc or doc.Name != cls.DOC_NAME: doc = App.newDocument(cls.DOC_NAME)
        return doc
    @classmethod
    def clear_all_panels(cls, doc):
        keep = {"Carcass", "Dividers", "Shelves", "Drawers", "Doors", "Hardware"}
        to_remove = [obj.Name for obj in doc.Objects if obj.TypeId == "Part::Feature" and obj.Name not in keep]
        for name in reversed(to_remove):
            try: doc.removeObject(name)
            except Exception as e: logger.warning(f"Cannot remove {name}: {e}")
