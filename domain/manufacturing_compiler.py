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

            identity_metadata = {
                "hardware_family": getattr(hardware_spec, "hardware_family", ""),
                "hardware_sku": sku,
                "hardware_intent": getattr(placement, "hardware_intent", ""),
                "hardware_description": getattr(
                    hardware_spec,
                    "display_name",
                    "",
                ),
                "hardware_category": getattr(
                    hardware_spec,
                    "hardware_family",
                    "",
                ) or getattr(hardware_spec, "category", ""),
                "hardware_unit": "pcs",
                "component_reference": getattr(
                    placement,
                    "component_reference",
                    "",
                ) or getattr(placement, "target_node_id", "") or getattr(
                    placement,
                    "host_node_id",
                    "",
                ),
                "cabinet_reference": getattr(
                    placement,
                    "cabinet_reference",
                    "",
                ),
                "source_operation_reference": getattr(
                    placement,
                    "source_operation_reference",
                    "",
                ),
                "hinge_family": getattr(placement, "hinge_family", ""),
                "hinge_side": getattr(placement, "hinge_side", ""),
                "hardware_ordinal": getattr(placement, "hinge_ordinal", 0),
                "resolved_hinge_count": getattr(
                    placement,
                    "resolved_hinge_count",
                    0,
                ),
            }
            
            # Host Processing (مثال: جانب الخزانة)
            host_node = project.graph.get_node(placement.host_node_id)
            if host_node and hardware_spec.host_holes:
                self._inject_operations(
                    host_node,
                    placement.anchor,
                    hardware_spec.host_holes,
                    identity_metadata,
                )
                
            # Target Processing (مثال: الرف)
            target_node_id = getattr(placement, 'target_node_id', None)
            if target_node_id:
                target_node = project.graph.get_node(target_node_id)
                if target_node and hardware_spec.target_holes:
                    self._inject_operations(
                        target_node,
                        placement.anchor,
                        hardware_spec.target_holes,
                        identity_metadata,
                    )

    def _inject_operations(self, node, anchor, hole_specs, identity_metadata=None):
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
                    op_type="DRILL", diameter=hole.diameter, depth=hole.depth, face=f_face,
                    local_x=resolved.local_x, local_y=resolved.local_y, 
                    axis=getattr(hole, 'axis', 'Z'), is_through=getattr(hole, 'is_through_hole', False),
                    metadata=dict(identity_metadata or {}),
                )
                node.machining_ops.append(op)
