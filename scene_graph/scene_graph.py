from typing import List, Dict, Optional
from scene_graph.node import SceneNode

class SceneGraph:
    """
    شجرة التصميم مع محرك بحث O(1) للأداء الصناعي
    """

    def __init__(self):
        self.nodes: List[SceneNode] = []
        self._identity_map: Dict[str, SceneNode] = {}
        self._by_role = {}

    def add_node(self, node: SceneNode):
        self.nodes.append(node)
        uid = (
            node.identity.key
            if hasattr(node.identity, "key")
            else str(node.identity)
        )
        self._identity_map[uid] = node

        role = getattr(node, "role", None)

        if role not in self._by_role:
            self._by_role[role] = []

        self._by_role[role].append(node)

    def get_node(
        self,
        identity: str
    ) -> Optional[SceneNode]:
        return self._identity_map.get(identity)

    def all_nodes(self) -> List[SceneNode]:
        return self.nodes

    @property
    def physical_nodes(self):
        return self.nodes

    @property
    def virtual_nodes(self):
        return []

    @property
    def hardware_nodes(self):
        return []
