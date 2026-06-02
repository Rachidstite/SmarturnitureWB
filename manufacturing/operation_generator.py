from domain.manufacturing_ops import ManufacturingOperation
from assembly.joint_rules import RULES

class OperationGenerator:

    @staticmethod
    def generate(assembly_graph):

        ops = []

        for joint in assembly_graph.all_joints():

            for rule in RULES:

                if (
                    rule.parent_role in joint.parent
                    or rule.child_role in joint.child
                ):

                    ops.append(
                        ManufacturingOperation(
                            operation_type="DRILL_MINIFIX"
                        )
                    )

        return ops
