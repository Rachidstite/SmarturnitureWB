from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class AssemblyEdge:
    """يمثل وصلة التجميع بين لوحين"""
    source_id: str      # اللوح الأساسي (مثلاً الجانب)
    target_id: str      # اللوح الفرعي (مثلاً الرف)
    connector: str      # نوع الوصلة (MINIFIX_15, CONFIRMAT_50, DOWEL_8x30)
    instruction: str = "" # تعليق إضافي للنجار

class PartLabeler:
    """يولد أكواد صناعية قصيرة للقطع لتسهيل قراءتها على الملصقات"""
    PREFIX_MAP = {
        "SIDE_PANEL": "S",
        "BOTTOM_PANEL": "B",
        "TOP_PANEL": "T",
        "SHELF": "SH",
        "BACK_PANEL": "BK",
        "DOOR_PANEL": "D",
        "DRAWER_FRONT": "DF",
        "DRAWER_SIDE": "DS",
        "DRAWER_BOTTOM": "DB",
        "DIVIDER": "DV",
        "PLINTH": "P"
    }

    def __init__(self):
        self.counters = {prefix: 1 for prefix in self.PREFIX_MAP.values()}
        self.counters["MISC"] = 1
        self.identity_to_label = {}

    def assign_label(self, node) -> str:
        uid = node.identity.key if hasattr(node.identity, 'key') else str(node.identity)
        if uid in self.identity_to_label:
            return self.identity_to_label[uid]

        role_str = str(getattr(node, 'role', '')).split('.')[-1]
        prefix = self.PREFIX_MAP.get(role_str, "MISC")
        
        label = f"{prefix}-{self.counters[prefix]:02d}"
        self.counters[prefix] += 1
        self.identity_to_label[uid] = label
        
        return label

class JoineryGraph:
    """شبكة الوصلات: تدير العلاقات بين الألواح وتحدد تسلسل التجميع"""
    def __init__(self):
        self.edges: List[AssemblyEdge] = []
        self.dependencies: Dict[str, List[str]] = {} # Node -> Needs these nodes first

    def add_connection(self, source: str, target: str, connector: str, instruction: str = ""):
        self.edges.append(AssemblyEdge(source, target, connector, instruction))
        
        # لتحديد التسلسل، نفترض أن الـ target يجب أن يركب على الـ source
        if target not in self.dependencies:
            self.dependencies[target] = []
        self.dependencies[target].append(source)

    def get_assembly_sequence(self, all_node_ids: List[str]) -> List[str]:
        """توليد تسلسل مبدئي للتركيب (Topological Sort مبسط)"""
        sequence = []
        visited = set()
        
        # الألواح التي ليس لها اعتمادات (مثل القاعدة والجانب) تركب أولاً
        ready = [n for n in all_node_ids if not self.dependencies.get(n)]
        
        while ready:
            current = ready.pop(0)
            if current not in visited:
                sequence.append(current)
                visited.add(current)
                
                # البحث عن الألواح التي أصبحت جاهزة للتركيب
                for node in all_node_ids:
                    if node not in visited and node in self.dependencies:
                        deps = self.dependencies[node]
                        if all(d in visited for d in deps):
                            ready.append(node)
                            
        # إضافة أي ألواح متبقية (لحماية النظام من الحلقات الدائرية - Circular deps)
        for n in all_node_ids:
            if n not in visited:
                sequence.append(n)
                
        return sequence
