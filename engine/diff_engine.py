from dataclasses import dataclass, field
from typing import List, Dict, Set
from scene_graph.semantic_state import NodeFingerprints, SemanticStateBuilder

@dataclass
class ChangeClassification:
    geometry_changed: bool = False
    transform_changed: bool = False
    visual_changed: bool = False
    manufacturing_changed: bool = False

    @property
    def requires_rebuild(self) -> bool:
        return self.geometry_changed or self.manufacturing_changed

@dataclass
class DiffResult:
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    modified: Dict[str, ChangeClassification] = field(default_factory=dict)
    unchanged: List[str] = field(default_factory=list)

    @property
    def requires_update(self) -> bool:
        return bool(self.added or self.removed or self.modified)

class SceneGraphDiffEngine:
    @classmethod
    def compute_diff(cls, old_graph, new_graph) -> DiffResult:
        old_map = cls._build_state_map(old_graph)
        new_map = cls._build_state_map(new_graph)

        old_ids = set(old_map.keys())
        new_ids = set(new_map.keys())

        added = list(new_ids - old_ids)
        removed = list(old_ids - new_ids)
        modified = {}
        unchanged = []

        for uid in old_ids.intersection(new_ids):
            old_fp = old_map[uid]
            new_fp = new_map[uid]
            
            if old_fp != new_fp:
                modified[uid] = ChangeClassification(
                    geometry_changed=(old_fp.geometry != new_fp.geometry),
                    transform_changed=(old_fp.transform != new_fp.transform),
                    visual_changed=(old_fp.visual != new_fp.visual),
                    manufacturing_changed=(old_fp.manufacturing != new_fp.manufacturing)
                )
            else:
                unchanged.append(uid)

        return DiffResult(added, removed, modified, unchanged)

    @staticmethod
    def _build_state_map(graph) -> Dict[str, NodeFingerprints]:
        if not graph: return {}
        return {
            (node.identity.key if hasattr(node.identity, 'key') else str(node.identity)): SemanticStateBuilder.build(node)
            for node in getattr(graph, 'nodes', [])
        }
