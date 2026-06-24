from dataclasses import dataclass, field, asdict
from typing import List, Optional, Tuple, Dict
from domain.topology import CabinetTopologyManager, Transform3D
from domain.core_types import NodeRole, JoineryType, NodeCategory

@dataclass
class Identity:
    key: str

@dataclass
class SceneNode:
    identity: Identity
    role: NodeRole
    width: float
    height: float
    thickness: float
    material: str
    edge_bands: dict = field(default_factory=dict)
    grain_direction: str = "VERTICAL"
    transform: Transform3D = field(default_factory=Transform3D)
    category: NodeCategory = NodeCategory.PHYSICAL
    machining_ops: list = field(default_factory=list)

    @property
    def group(self):
        return getattr(self.role, "value", str(self.role))

    @property
    def edge_spec(self):
        return None

    def to_dict(self) -> dict:
        return {
            "identity": {"key": self.identity.key},
            "role": self.role.value if hasattr(self.role, 'value') else self.role,
            "width": self.width,
            "height": self.height,
            "thickness": self.thickness,
            "material": self.material,
            "edge_bands": self.edge_bands,
            "grain_direction": self.grain_direction,
            "transform": asdict(self.transform),
            "category": self.category.value if hasattr(self.category, 'value') else self.category,
            "machining_ops": [op.to_dict() for op in getattr(self, "machining_ops", [])]
        }

@dataclass
class VirtualAnchor:
    identity: Identity
    role: NodeRole = NodeRole.VIRTUAL_ANCHOR
    transform: Transform3D = field(default_factory=Transform3D)
    category: NodeCategory = NodeCategory.VIRTUAL

    def to_dict(self) -> dict:
        return {
            "identity": {"key": self.identity.key},
            "role": self.role.value if hasattr(self.role, 'value') else self.role,
            "transform": asdict(self.transform),
            "category": self.category.value if hasattr(self.category, 'value') else self.category
        }

class SceneGraph:
    def __init__(self):
        self.nodes = []
        self._by_id: Dict[str, any] = {}
        self._by_category: Dict[NodeCategory, List[any]] = {cat: [] for cat in NodeCategory}
        self._by_role: Dict[NodeRole, List[any]] = {role: [] for role in NodeRole}

    def add_node(self, node):
        uid = node.identity.key
        if uid in self._by_id:
            raise ValueError(f"CRITICAL: Duplicate Node Identity detected: {uid}. Graph Integrity Violated!")
            
        self.nodes.append(node)
        self._by_id[uid] = node
        self._by_category[node.category].append(node)
        self._by_role[node.role].append(node)

    def get_node(self, uid: str):
        return self._by_id.get(uid)

    @property
    def physical_nodes(self): return self._by_category[NodeCategory.PHYSICAL]
    @property
    def virtual_nodes(self): return self._by_category[NodeCategory.VIRTUAL]
    @property
    def hardware_nodes(self): return self._by_category[NodeCategory.HARDWARE]

    def all_nodes(self):
        return self.nodes

@dataclass
class CabinetProject:
    graph: SceneGraph
    joinery: any
    topology: any
    placements: list = field(default_factory=list)

class WardrobeBuilder:
    def __init__(self, uid: str, width: float, height: float, depth: float, thickness: float = 18.0, material: str = "MDF_18_WHITE"):
        self.uid = uid
        self.w = width
        self.h = height
        self.d = depth
        self.t = thickness
        self.mat = material
        
        from domain.assembly_graph import JoineryGraph
        self.joinery = JoineryGraph()
        self.graph = SceneGraph()
        
        self.topology = CabinetTopologyManager(
            inner_width=self.w - (2 * self.t),
            inner_height=self.h - (2 * self.t),
            inner_depth=self.d,
            thickness=self.t
        )
        
        self.shelf_anchor = VirtualAnchor(Identity(f"{self.uid}_WALL_ANCHOR"))
        self.graph.add_node(self.shelf_anchor)
        self._build_carcass()

    def _build_carcass(self):
        edges = {"FRONT": "ABS_1MM", "TOP": "ABS_1MM", "BOTTOM": "ABS_1MM"}
        self.left_side = SceneNode(Identity(f"{self.uid}_SIDE_L"), NodeRole.SIDE_PANEL, self.d, self.h, self.t, self.mat, edges, transform=Transform3D(x=0, y=0, z=0))
        self.right_side = SceneNode(Identity(f"{self.uid}_SIDE_R"), NodeRole.SIDE_PANEL, self.d, self.h, self.t, self.mat, edges, transform=Transform3D(x=self.w - self.t, y=0, z=0))
        
        inner_w = self.w - (2 * self.t)
        self.bottom = SceneNode(Identity(f"{self.uid}_BOTTOM"), NodeRole.BOTTOM_PANEL, inner_w, self.d, self.t, self.mat, edges, "HORIZONTAL", transform=Transform3D(x=self.t, y=0, z=0))
        self.top = SceneNode(Identity(f"{self.uid}_TOP"), NodeRole.TOP_PANEL, inner_w, self.d, self.t, self.mat, edges, "HORIZONTAL", transform=Transform3D(x=self.t, y=0, z=self.h - self.t))

        self.back = SceneNode(
            Identity(f"{self.uid}_BACK"),
            NodeRole.BACK_PANEL,
            self.w - self.t,
            self.h - self.t,
            3.0,
            "HDF_3MM",
            {},
            "VERTICAL",
            transform=Transform3D(x=self.t / 2, y=15, z=self.t / 2)
        )

        
        for n in [self.left_side, self.right_side, self.bottom, self.top, self.back]:
            self.graph.add_node(n)
        
        self.joinery.add_connection(self.left_side.identity.key, self.bottom.identity.key, JoineryType.MINIFIX_15.value)
        self.joinery.add_connection(self.right_side.identity.key, self.bottom.identity.key, JoineryType.MINIFIX_15.value)
        self.joinery.add_connection(self.left_side.identity.key, self.top.identity.key, JoineryType.MINIFIX_15.value)
        self.joinery.add_connection(self.right_side.identity.key, self.top.identity.key, JoineryType.MINIFIX_15.value)


    def add_divider(self, x_offset: float, section_id: str = "ROOT") -> Tuple[str, str]:

        div_uid, left_id, right_id = self.topology.add_vertical_divider(
            x_offset,
            self.t,
            section_id
        )

        section = self.topology.get_section(left_id)

        inner_h = self.h - (2 * self.t)

        div_key = f"{self.uid}_{div_uid}"

        absolute_x = self.t + section.origin_x + section.width

        div = SceneNode(
            Identity(div_key),
            NodeRole.DIVIDER,
            self.d - 20,
            inner_h,
            self.t,
            self.mat,
            {"FRONT": "ABS_1MM"},
            "VERTICAL",
            transform=Transform3D(
                x=absolute_x,
                y=0,
                z=self.t
            )
        )

        self.graph.add_node(div)

        self.joinery.add_connection(
            self.bottom.identity.key,
            div_key,
            JoineryType.CONFIRMAT_50.value
        )

        self.joinery.add_connection(
            self.top.identity.key,
            div_key,
            JoineryType.CONFIRMAT_50.value
        )

        return left_id, right_id

    def add_shelves(self, count: int, section_id: str):
        section = self.topology.get_section(section_id)
        sec_w = section.width
        start_x = section.origin_x
        
        vertical_gap = (section.height - (count * self.t)) / (count + 1)
        current_z = vertical_gap
        
        for i in range(count):
            shelf_key = f"{self.uid}_SH_{section_id}_{i+1}"
            shelf = SceneNode(
                Identity(shelf_key), NodeRole.SHELF, 
                sec_w - 1, self.d - 20, self.t, self.mat, 
                {"FRONT": "ABS_1MM"}, "HORIZONTAL",
                transform=Transform3D(x=self.t + start_x, y=0, z=self.t + current_z)
            )
            self.graph.add_node(shelf)
            current_z += self.t + vertical_gap
            self.joinery.add_connection(self.shelf_anchor.identity.key, shelf_key, JoineryType.SHELF_PIN_5MM.value, "Virtual Anchor support")

    def add_doors(self, count: int, material: str = "MDF_18_OAK"):
        from domain.layout_engine import DoorClusterEngine
        total_opening = self.w - (2 * self.t)
        door_specs = DoorClusterEngine.compute_layout(total_opening, count)
        
        for i, spec in enumerate(door_specs):
            door_h = self.h - 4 
            door = SceneNode(
                Identity(f"{self.uid}_DOOR_{i+1}"), NodeRole.DOOR_PANEL, 
                spec.width, door_h, self.t, material, 
                {"TOP": "ABS_1MM", "BOTTOM": "ABS_1MM", "LEFT": "ABS_1MM", "RIGHT": "ABS_1MM"},
                "VERTICAL",
                transform=Transform3D(x=self.t + spec.x_position, y=self.d, z=2)
            )
            self.graph.add_node(door)

    def build(self) -> CabinetProject:
        return CabinetProject(graph=self.graph, joinery=self.joinery, topology=self.topology, placements=[])
