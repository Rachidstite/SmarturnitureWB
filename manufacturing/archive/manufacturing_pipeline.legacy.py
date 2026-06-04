from assembly.assembly_graph_builder import AssemblyGraphBuilder
from manufacturing.joint_operation_generator import JointOperationGenerator

class ManufacturingPipeline:

    @staticmethod
    def generate(scene_graph):

        assembly = AssemblyGraphBuilder.build(scene_graph)

        operations = []

        for joint in assembly.all_joints():

            if joint.joint_type != "MINIFIX":
                continue

            parent_node = scene_graph.get_node(
                joint.parent
            )

            child_node = scene_graph.get_node(
                joint.child
            )

            if not parent_node or not child_node:
                continue

            operations.extend(
                JointOperationGenerator.minifix_joint(
                    parent_node,
                    child_node
                )
            )

        return operations
