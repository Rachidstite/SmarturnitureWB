import hashlib
import json
from dataclasses import dataclass

@dataclass(frozen=True)
class NodeFingerprints:
    geometry: str
    transform: str
    visual: str
    manufacturing: str

class SemanticStateBuilder:
    """
    Explicit Fingerprint Builders:
    يبني بصمات مستقلة لكل قناة دلالية لتجنب التحديث الأعمى.
    """
    @classmethod
    def build(cls, node) -> NodeFingerprints:
        return NodeFingerprints(
            geometry=cls._hash_geom(node),
            transform=cls._hash_transform(node),
            visual=cls._hash_visual(node),
            manufacturing=cls._hash_mfg(node)
        )

    @staticmethod
    def _hash_obj(data_dict: dict) -> str:
        state_json = json.dumps(data_dict, sort_keys=True, default=str) # default=str لحماية json
        return hashlib.sha256(state_json.encode('utf-8')).hexdigest()

    @classmethod
    def _hash_geom(cls, node) -> str:
        return cls._hash_obj({
            "w": getattr(node, 'width', 0),
            "h": getattr(node, 'height', 0),
            "t": getattr(node, 'thickness', 0)
        })

    @classmethod
    def _hash_transform(cls, node) -> str:
        return cls._hash_obj({
            "tr": getattr(node, 'transform', [])
        })

    @classmethod
    def _hash_visual(cls, node) -> str:
        return cls._hash_obj({
            "mat": getattr(node, 'material', ""),
            "grp": getattr(node, 'group', "")
        })

    @classmethod
    def _hash_mfg(cls, node) -> str:
        # سيتم دمج عمليات CNC هنا لاحقاً
        return cls._hash_obj({
            "edge": getattr(node, 'edge_bands', {}),
            "cnc": getattr(node, 'cnc_operations', []) if hasattr(node, 'cnc_operations') else [],
            "ops": getattr(node, 'manufacturing_ops', []) if hasattr(node, 'manufacturing_ops') else []
        })
