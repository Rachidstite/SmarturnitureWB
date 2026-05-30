from typing import List, Dict, Optional
from scene_graph.node import SceneNode

class SceneGraph:
    """
    شجرة التصميم مع محرك بحث O(1) للأداء الصناعي
    """
    def __init__(self):
        self.nodes: List[SceneNode] = []
        self._identity_map: Dict[str, SceneNode] = {}

    def add_node(self, node: SceneNode):
        self.nodes.append(node)
        uid = node.identity.key if hasattr(node.identity, 'key') else str(node.identity)
        self._identity_map[uid] = node

    def get_node(self, identity: str) -> Optional[SceneNode]:
        """بحث سريع O(1) يمنع عنق الزجاجة O(n^2)"""
        return self._identity_map.get(identity)

    def all_nodes(self) -> List[SceneNode]:
        return self.nodes
