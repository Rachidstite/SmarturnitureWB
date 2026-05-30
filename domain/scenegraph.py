from typing import Optional, List, Dict
from domain.entities import SceneNode
from domain.core_types import NodeRole, NodeCategory

class SceneGraph:
    """
    Indexed Scene Graph
    Compatible with:
    - rules_engine
    - serialization
    - constraint_engine
    - manufacturing_compiler
    """

    def __init__(self):
        self.nodes: List[SceneNode] = []

        self._by_id: Dict[str, SceneNode] = {}

        self._by_role: Dict[NodeRole, List[SceneNode]] = {
            role: [] for role in NodeRole
        }

    def add_node(self, node: SceneNode):

        if node.identity.key in self._by_id:
            raise ValueError(
                f"CRITICAL: Duplicate Node Identity detected: "
                f"{node.identity.key}"
            )

        self.nodes.append(node)

        self._by_id[node.identity.key] = node

        if node.role not in self._by_role:
            self._by_role[node.role] = []

        self._by_role[node.role].append(node)

    def get_node(self, key: str) -> Optional[SceneNode]:
        return self._by_id.get(key)

    @property
    def physical_nodes(self) -> List[SceneNode]:
        return self.nodes

    @property
    def virtual_nodes(self) -> List[SceneNode]:
        return []

    @property
    def hardware_nodes(self) -> List[SceneNode]:
        return []
