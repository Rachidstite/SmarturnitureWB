from copy import deepcopy

from domain.hardware_library import HardwareRegistry
from domain.manufacturing_ops import FaceDrill, EdgeDrill
from manufacturing.hardware_operation_adapter import (
    HardwareOperationAdapter,
)

class JointOperationGenerator:

    @staticmethod
    def minifix_joint(parent_node, child_node, hardware_profile=None):
        profile = dict(hardware_profile or {})
        if not profile:
            from domain.rules_engine import RuleContext

            profile = dict(RuleContext().hardware_profile or {})

        sku = profile.get("INTENT_MINIFIX_15", "MINIFIX_15_V1")
        hardware_spec = HardwareRegistry().get_hardware(sku)
        hardware_family = str(
            getattr(hardware_spec, "hardware_family", "") or "MINIFIX"
        )
        metadata = {
            "hardware_family": hardware_family,
            "hardware_sku": sku,
            "hardware_intent": "INTENT_MINIFIX_15",
        }

        ops = []

        # Cam 15mm
        ops.append(
            FaceDrill(
                x=34,
                y=64,
                diameter=15,
                depth=12,
                face="TOP",
                metadata=dict(metadata),
            )
        )

        # Dowel hole
        ops.append(
            EdgeDrill(
                x=64,
                z=(parent_node.thickness / 2),
                diameter=8,
                depth=30,
                edge="TOP",
                metadata=dict(metadata),
            )
        )

        return ops

    @staticmethod
    def minifix_joint_from_hardware(parent_node, child_node, hardware_spec):
        metadata = {
            "hardware_family": getattr(hardware_spec, "hardware_family", ""),
            "hardware_sku": getattr(hardware_spec, "sku", ""),
            "hardware_intent": "INTENT_MINIFIX_15",
        }
        return HardwareOperationAdapter.to_unified(
            deepcopy(hardware_spec.target_holes)
        )
