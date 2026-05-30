from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class CutlistItem:
    identity: str
    material: str
    finished_width: float
    finished_height: float
    thickness: float
    edge_bands: Dict[str, str]
    cut_width: float = 0.0
    cut_height: float = 0.0
    grain_direction: str = "NONE"

@dataclass
class CNCProgram:
    identity: str
    material: str
    thickness: float
    dimensions: tuple  # (X, Y)
    face_drills: List[Any] = field(default_factory=list)
    edge_drills: List[Any] = field(default_factory=list)
    grooves: List[Any] = field(default_factory=list)

class ProductionEngine:
    """
    جسر العبور من الـ CAD إلى أرض المصنع.
    """
    
    # سماكة شرائط اللصق الافتراضية (يجب أن تأتي من مكتبة المواد لاحقاً)
    EDGE_THICKNESS_MAP = {
        "ABS_1MM": 1.0,
        "ABS_2MM": 2.0,
        "PVC_0.4MM": 0.4,
        "NONE": 0.0,
        None: 0.0
    }

    @classmethod
    def generate_cutlist(cls, scene_graph) -> List[CutlistItem]:
        """يولد قائمة القص مع خصم سماكة شرائط اللصق"""
        cutlist = []
        for node in getattr(scene_graph, 'physical_nodes', []):
            # الفلترة: نأخذ فقط الألواح (نتجاهل HardwareNodes)
            role_str = str(getattr(node, 'role', ''))
            if "HARDWARE" in role_str or getattr(node, 'material', None) is None:
                continue
                
            edges = getattr(node, 'edge_bands', {})
            fw = getattr(node, 'width', 0)
            fh = getattr(node, 'height', 0)
            
            # خصم الحواف من العرض (يمين + يسار)
            w_deduction = cls.EDGE_THICKNESS_MAP.get(edges.get("LEFT"), 0) + \
                          cls.EDGE_THICKNESS_MAP.get(edges.get("RIGHT"), 0)
            
            # خصم الحواف من الارتفاع/العمق (أعلى + أسفل)
            h_deduction = cls.EDGE_THICKNESS_MAP.get(edges.get("TOP"), 0) + \
                          cls.EDGE_THICKNESS_MAP.get(edges.get("BOTTOM"), 0)

            item = CutlistItem(
                identity=node.identity.key if hasattr(node.identity, 'key') else str(node.identity),
                material=node.material,
                finished_width=fw,
                finished_height=fh,
                thickness=getattr(node, 'thickness', 0),
                edge_bands=edges,
                cut_width=fw - w_deduction,
                cut_height=fh - h_deduction
            )
            cutlist.append(item)
        return cutlist

    @classmethod
    def generate_cnc_data(cls, scene_graph) -> Dict[str, CNCProgram]:
        """يستخرج العمليات التصنيعية لكل لوح ويجهزها للتصدير للماكينة"""
        cnc_programs = {}
        for node in getattr(scene_graph, 'physical_nodes', []):
            ops = getattr(node, 'manufacturing_ops', [])
            if not ops:
                continue # لوح بدون عمليات تصنيع، يحتاج قص فقط
                
            uid = node.identity.key if hasattr(node.identity, 'key') else str(node.identity)
            
            program = CNCProgram(
                identity=uid,
                material=node.material,
                thickness=node.thickness,
                dimensions=(getattr(node, 'width', 0), getattr(node, 'height', 0))
            )
            
            # تصنيف العمليات حسب النوع (Routing / Drilling)
            for op in ops:
                op_type = type(op).__name__
                if op_type == "FaceDrill":
                    program.face_drills.append(op)
                elif op_type == "EdgeDrill":
                    program.edge_drills.append(op)
                elif op_type == "Groove":
                    program.grooves.append(op)
                    
            cnc_programs[uid] = program
            
        return cnc_programs
