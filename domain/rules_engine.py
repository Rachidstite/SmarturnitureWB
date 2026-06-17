from dataclasses import dataclass, field
from typing import List, Dict
from domain.builders import CabinetProject
from domain.core_types import NodeRole, JoineryType
from domain.anchors import HardwarePlacement, AnchorCoordinate, MountFace, EdgeRef

@dataclass
class RuleContext:
    """السياق الصناعي الذي يحدد طبيعة عمل القواعد"""
    market_region: str = "MOROCCO"
    preferred_connector: JoineryType = JoineryType.CONFIRMAT_50
    cnc_capabilities: str = "3_AXIS"
    material_thickness: float = 18.0
    # Hardware Profile Mapping
    hardware_profile: Dict[str, str] = field(default_factory=lambda: {
        "INTENT_HINGE": "HINGE_BLUM_110_V1",
        "INTENT_MINIFIX_15": "MINIFIX_15_V1",
        "INTENT_CONFIRMAT_50": "CONFIRMAT_50_V1",
        "INTENT_SHELF_PIN": "SHELF_PIN_5MM",
        "INTENT_DRAWER_SLIDE": "DRAWER_SLIDE_SOFTCLOSE_450",
        "INTENT_HANDLE": "HANDLE_128_BLACK",
    })


def build_rule_context_from_params(params, base_context=None):
    if base_context is None:
        context = RuleContext()
    else:
        context = RuleContext(
            market_region=base_context.market_region,
            preferred_connector=base_context.preferred_connector,
            cnc_capabilities=base_context.cnc_capabilities,
            material_thickness=base_context.material_thickness,
            hardware_profile=dict(getattr(base_context, "hardware_profile", {}) or {}),
        )

    hinge_sku = getattr(params, "hinge_sku", None)
    if hinge_sku:
        context.hardware_profile["INTENT_HINGE"] = hinge_sku

    slide_sku = getattr(params, "slide_sku", None)
    if slide_sku:
        context.hardware_profile["INTENT_DRAWER_SLIDE"] = slide_sku

    handle_sku = getattr(params, "handle_sku", None)
    if handle_sku:
        context.hardware_profile["INTENT_HANDLE"] = handle_sku

    return context

class HardwareRule:
    """الفئة الأساسية لأي قاعدة تصنيعية"""
    def apply(self, project: CabinetProject, context: RuleContext) -> List[HardwarePlacement]:
        raise NotImplementedError

class HingeRule(HardwareRule):
    """قاعدة توزيع المفصلات بناءً على ارتفاع الباب"""
    def apply(self, project: CabinetProject, context: RuleContext) -> List[HardwarePlacement]:
        placements = []
        doors = project.graph._by_role.get(NodeRole.DOOR_PANEL, [])
        
        for door in doors:
            height = door.height
            if height < 900:
                hinge_count = 2
            elif height <= 1600:
                hinge_count = 3
            else:
                hinge_count = 4
                
            offsets = [100.0, height - 100.0]
            if hinge_count == 3:
                offsets.insert(1, height / 2.0)
            elif hinge_count == 4:
                step = (height - 200.0) / 3.0
                offsets.insert(1, 100.0 + step)
                offsets.insert(2, 100.0 + 2 * step)
                
            for i, offset_z in enumerate(offsets):
                placements.append(HardwarePlacement(
                    host_node_id=door.identity.key,
                    hardware_intent="INTENT_HINGE",
                    anchor=AnchorCoordinate(
                        face=MountFace.BACK, 
                        edge=EdgeRef.BOTTOM, 
                        offset_x=22.0, 
                        offset_y=offset_z
                    ),
                    description=f"Hinge {i+1}/{hinge_count}"
                ))
        return placements

class System32JoineryRule(HardwareRule):
    """قاعدة توزيع أدوات التجميع بنظام الـ 32 ملم الصناعي"""
    def apply(self, project: CabinetProject, context: RuleContext) -> List[HardwarePlacement]:
        placements = []
        for edge in project.joinery.edges:
            if edge.connector in [JoineryType.MINIFIX_15.value, JoineryType.CONFIRMAT_50.value]:
                depth = 580.0 
                
                placements.append(HardwarePlacement(
                    host_node_id=edge.target_id,
                    target_node_id=edge.source_id,
                    hardware_intent=f"INTENT_{edge.connector}",
                    anchor=AnchorCoordinate(MountFace.LEFT, EdgeRef.FRONT, offset_x=0, offset_y=50.0),
                    description="Front joint anchor"
                ))
                
                placements.append(HardwarePlacement(
                    host_node_id=edge.target_id,
                    target_node_id=edge.source_id,
                    hardware_intent=f"INTENT_{edge.connector}",
                    anchor=AnchorCoordinate(MountFace.LEFT, EdgeRef.BACK, offset_x=0, offset_y=50.0),
                    description="Back joint anchor"
                ))
                
                if depth > 400:
                    placements.append(HardwarePlacement(
                        host_node_id=edge.target_id,
                        target_node_id=edge.source_id,
                        hardware_intent=f"INTENT_{edge.connector}",
                        anchor=AnchorCoordinate(MountFace.LEFT, EdgeRef.CENTER, offset_x=0, offset_y=0.0),
                        description="Center joint anchor"
                    ))
        return placements

class ShelfSupportRule(HardwareRule):
    """قاعدة توزيع مسامير الأرفف (4 مسامير لكل رف)"""
    def apply(self, project: CabinetProject, context: RuleContext) -> List[HardwarePlacement]:
        placements = []
        for edge in project.joinery.edges:
            if edge.connector == JoineryType.SHELF_PIN_5MM.value:
                # 4 مسامير لكل رف (أمام وخلف، يمين ويسار)
                # للتبسيط، نعتبر أن الـ Host هو الـ Virtual Anchor
                for face in [MountFace.LEFT, MountFace.RIGHT]:
                    for edge_ref in [EdgeRef.FRONT, EdgeRef.BACK]:
                        placements.append(HardwarePlacement(
                            host_node_id=edge.source_id,
                            target_node_id=edge.target_id,
                            hardware_intent="INTENT_SHELF_PIN",
                            anchor=AnchorCoordinate(face, edge_ref, offset_x=0, offset_y=50.0)
                        ))
        return placements

class DrawerSlideRule(HardwareRule):
    """قاعدة توزيع شرائح الأدراج (شريحتان لكل واجهة درج)"""
    def apply(self, project: CabinetProject, context: RuleContext) -> List[HardwarePlacement]:
        placements = []
        drawers = self._drawer_faces_from_graph(project.graph)

        for drawer in drawers:
            placements.append(HardwarePlacement(
                host_node_id=drawer.identity.key,
                hardware_intent="INTENT_DRAWER_SLIDE",
                anchor=AnchorCoordinate(MountFace.LEFT, EdgeRef.FRONT, offset_x=0, offset_y=0.0),
                description="Left drawer slide"
            ))
            placements.append(HardwarePlacement(
                host_node_id=drawer.identity.key,
                hardware_intent="INTENT_DRAWER_SLIDE",
                anchor=AnchorCoordinate(MountFace.RIGHT, EdgeRef.FRONT, offset_x=0, offset_y=0.0),
                description="Right drawer slide"
            ))
        return placements

    @staticmethod
    def _drawer_faces_from_graph(graph):
        by_role = getattr(graph, "_by_role", {}) or {}
        candidates = []
        for role_key, nodes in by_role.items():
            role_name = getattr(role_key, "name", None)
            role_value = getattr(role_key, "value", None)
            role_text = str(role_key).split(".")[-1]
            if role_name == "DRAWER_FACE" or role_value == "DRAWER_FACE" or role_text == "DRAWER_FACE":
                candidates.extend(nodes or [])
        return candidates

class HandleRule(HardwareRule):
    """قاعدة توزيع المقابض الأساسية لكل باب أو واجهة درج"""
    def apply(self, project: CabinetProject, context: RuleContext) -> List[HardwarePlacement]:
        placements = []
        for panel in self._handle_panels_from_graph(project.graph):
            placements.append(HardwarePlacement(
                host_node_id=panel.identity.key,
                hardware_intent="INTENT_HANDLE",
                anchor=AnchorCoordinate(
                    MountFace.FRONT,
                    EdgeRef.CENTER,
                    offset_x=0.0,
                    offset_y=0.0,
                ),
                description="Handle",
            ))
        return placements

    @staticmethod
    def _handle_panels_from_graph(graph):
        by_role = getattr(graph, "_by_role", {}) or {}
        candidates = []
        for role_key, nodes in by_role.items():
            role_name = getattr(role_key, "name", None)
            role_value = getattr(role_key, "value", None)
            role_text = str(role_key).split(".")[-1]
            if role_name in ("DOOR_PANEL", "DRAWER_FRONT") or role_value in ("DOOR_PANEL", "DRAWER_FRONT") or role_text in ("DOOR_PANEL", "DRAWER_FRONT"):
                candidates.extend(nodes or [])
        return candidates

class HardwarePlacementEngine:
    """المحرك الذي يطبق جميع القواعد ويحقن النوايا (Intents) في المشروع"""
    def __init__(self, context: RuleContext = None):
        self.context = context or RuleContext()
        self.rules: List[HardwareRule] = [
            HingeRule(),
            System32JoineryRule(),
            ShelfSupportRule(),
            HandleRule(),
            DrawerSlideRule()
        ]

    def process(self, project: CabinetProject):
        for rule in self.rules:
            new_placements = rule.apply(project, self.context)
            project.placements.extend(new_placements)
