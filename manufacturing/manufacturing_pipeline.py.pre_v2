from assembly.assembly_graph_builder import AssemblyGraphBuilder
from manufacturing.joint_operation_generator import JointOperationGenerator

class ManufacturingPipeline:

    @staticmethod
    def generate(scene_graph):

        assembly = AssemblyGraphBuilder.build(scene_graph)

        operations = []

        for joint in assembly.all_joints():

            if joint.joint_type == "MINIFIX":

                operations.extend(
                    JointOperationGenerator.minifix_joint()
                )

        return operations
