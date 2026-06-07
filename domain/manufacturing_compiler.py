from domain.builders import CabinetProject
from domain.hardware_library import HardwareRegistry
from domain.core_types import MachiningOperation
from domain.resolvers import CoordinateResolver
from domain.rules_engine import RuleContext

class ManufacturingCompiler:
    """يحول نوايا التثبيت (Placements) إلى عمليات ثقب فعلية (MachiningOps)"""
    
    def __init__(self):
        self.registry = HardwareRegistry()

    def compile(self, project: CabinetProject, context: RuleContext):
        for placement in getattr(project, 'placements', []):
            # Dynamic Profile Mapping
            sku = context.hardware_profile.get(placement.hardware_intent)
            if not sku: 
                continue
            
            hardware_spec = self.registry.get_hardware(sku)
            if not hardware_spec: 
                continue
            
            # Host Processing (مثال: جانب الخزانة)
            host_node = project.graph.get_node(placement.host_node_id)
            if host_node and hardware_spec.host_holes:
                self._inject_operations(host_node, placement, placement.anchor, hardware_spec.host_holes)
                
            # Target Processing (مثال: الرف)
            target_node_id = getattr(placement, 'target_node_id', None)
            if target_node_id:
                target_node = project.graph.get_node(target_node_id)
                if target_node and hardware_spec.target_holes:
                    self._inject_operations(target_node, placement, placement.anchor, hardware_spec.target_holes)

    def _inject_operations(self, node, placement, anchor, hole_specs):
        if not hasattr(node, 'machining_ops'):
            node.machining_ops = []
            
        from domain.resolvers import CoordinateResolver
        from domain.core_types import MachiningOperation
        
        for hole in hole_specs:
            resolved = CoordinateResolver.resolve(node, anchor, hole.offset_x, hole.offset_y)
            face_val = hole.face.value if hasattr(hole.face, 'value') else str(hole.face)
            final_face = face_val if face_val else resolved.face
            
            # ⚡ تنظيف الوجه لضمان دقة المقارنة (مثلاً: MountFace.FRONT تصبح FRONT)
            f_face = str(final_face).split('.')[-1]
            
            is_dup = False
            for ex in node.machining_ops:
                e_face = str(ex.face).split('.')[-1]
                # مقارنة الوجه، الإحداثيات، والقطر بهامش خطأ بسيط
                if e_face == f_face and abs(ex.local_x - resolved.local_x) < 0.1 and abs(ex.local_y - resolved.local_y) < 0.1 and abs(ex.diameter - hole.diameter) < 0.1:
                    is_dup = True
                    break
                    
            if not is_dup:
                op = MachiningOperation(
                    op_type="DRILL",
                    diameter=hole.diameter,
                    depth=hole.depth,
                    face=f_face,
                    local_x=resolved.local_x,
                    local_y=resolved.local_y,
                    axis=getattr(hole, 'axis', 'Z'),
                    is_through=getattr(hole, 'is_through_hole', False),
                    metadata={
                        "hardware_intent": placement.hardware_intent,
                        "target_node_id": getattr(
                            placement,
                            "target_node_id",
                            None
                        )
                    }
                )
                node.machining_ops.append(op)
