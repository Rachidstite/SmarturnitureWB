import math
from typing import List, Dict, Optional
from scene_graph.node import SceneNode
from scene_graph.metadata import BackPanelMetadata

class SceneGraph:
    """
    شجرة التصميم مع محرك بحث O(1) للأداء الصناعي
    """
    def __init__(self):
        self.nodes: List[SceneNode] = []
        self._identity_map: Dict[str, SceneNode] = {}

    def _node_key(self, node: SceneNode) -> str:
        identity = getattr(node, "identity", None)
        key = identity.key if hasattr(identity, "key") else str(identity or "")
        key = key.strip()
        if not key:
            raise ValueError("SceneGraph node identity is required.")
        return key

    def add_node(self, node: SceneNode):
        uid = self._node_key(node)
        if uid in self._identity_map:
            raise ValueError(f"Duplicate SceneGraph identity: {uid}")
        self.nodes.append(node)
        self._identity_map[uid] = node

    def get_node(self, identity: str) -> Optional[SceneNode]:
        """بحث سريع O(1) يمنع عنق الزجاجة O(n^2)"""
        return self._identity_map.get(identity)

    def all_nodes(self) -> List[SceneNode]:
        return self.nodes

    def validate_integrity(self) -> bool:
        seen = set()
        for node in self.nodes:
            uid = self._node_key(node)
            if uid in seen:
                raise ValueError(f"Duplicate SceneGraph identity: {uid}")
            seen.add(uid)
            for attr in ("width", "depth", "height"):
                value = getattr(node, attr, None)
                if value is None or value <= 0:
                    raise ValueError(f"SceneGraph node {uid} has invalid {attr}: {value}")
            for attr in ("x", "y", "z"):
                value = getattr(node, attr, None)
                if value is None or not math.isfinite(value):
                    raise ValueError(f"SceneGraph node {uid} has invalid {attr}: {value}")
            if getattr(node, "role", None) is None:
                raise ValueError(f"SceneGraph node {uid} has no role.")
            if not getattr(node, "material", None):
                raise ValueError(f"SceneGraph node {uid} has no material.")
            if getattr(getattr(node, "role", None), "name", "") == "BACK_PANEL":
                self._validate_back_panel_node(uid, node)
        if set(self._identity_map.keys()) != seen:
            raise ValueError("SceneGraph identity index is out of sync with nodes.")
        return True

    def _validate_back_panel_node(self, uid: str, node: SceneNode):
        thickness = getattr(node, "thickness", None)
        if thickness is None or thickness <= 0:
            raise ValueError(f"Back panel node {uid} has invalid thickness: {thickness}")

        metadata = getattr(node, "metadata", None)
        if not isinstance(metadata, BackPanelMetadata):
            raise ValueError(f"Back panel node {uid} requires BackPanelMetadata.")

        if not isinstance(metadata.section_index, int) or metadata.section_index < 0:
            raise ValueError(f"Back panel node {uid} has invalid section_index: {metadata.section_index}")
        if not isinstance(metadata.section_label, str) or not metadata.section_label.strip():
            raise ValueError(f"Back panel node {uid} has invalid section_label: {metadata.section_label}")
        if metadata.groove_depth < 0:
            raise ValueError(f"Back panel node {uid} has invalid groove_depth: {metadata.groove_depth}")
        if metadata.back_offset < 0:
            raise ValueError(f"Back panel node {uid} has invalid back_offset: {metadata.back_offset}")
