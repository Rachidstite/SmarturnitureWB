import hashlib
import json
from dataclasses import is_dataclass, asdict
from enum import Enum

class NodeStateSerializer:
    """
    يحول الخصائص الصناعية للـ SceneNode إلى بصمة (Hash) 
    باستخدام Explicit Registry لضمان الاستقرار ومنع أخطاء str(obj).
    """
    @staticmethod
    def serialize(node) -> str:
        state_dict = {
            "role": str(getattr(node, 'role', '')),
            "width": getattr(node, 'width', 0),
            "height": getattr(node, 'height', 0),
            "thickness": getattr(node, 'thickness', 0),
            "material": getattr(node, 'material', ''),
            "edge_bands": getattr(node, 'edge_bands', {}),
            "group": getattr(node, 'group', ''),
        }

        def custom_encoder(obj):
            if isinstance(obj, Enum): 
                return {"__type__": "Enum", "value": obj.name}
            if is_dataclass(obj): 
                return {"__type__": type(obj).__name__, "value": asdict(obj)}
            if hasattr(obj, 'to_dict'):
                return {"__type__": type(obj).__name__, "value": obj.to_dict()}
            
            # Fallback آمن للأشياء الأساسية فقط
            if isinstance(obj, (int, float, str, bool, type(None))):
                return obj
                
            raise TypeError(f"Unregistered serialization for type: {type(obj)}")

        state_json = json.dumps(state_dict, default=custom_encoder, sort_keys=True)
        return hashlib.sha256(state_json.encode('utf-8')).hexdigest()
