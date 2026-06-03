from assembly.assembly_graph_builder import AssemblyGraphBuilder
from manufacturing.joint_operation_generator import JointOperationGenerator

class PanelOperationEngine:

    @staticmethod
    def generate(scene_graph):

        panel_ops = {}

        assembly = AssemblyGraphBuilder.build(scene_graph)

        for joint in assembly.all_joints():

            if joint.joint_type != "MINIFIX":
                continue

            ops = JointOperationGenerator.minifix_joint()

            panel_ops.setdefault(joint.parent, [])
            panel_ops[joint.parent].extend(ops)

        
        print("[PANEL OPS COUNT]", len(panel_ops))

        for k,v in panel_ops.items():
            print("[PANEL]", k, "OPS=", len(v))

        return panel_ops

