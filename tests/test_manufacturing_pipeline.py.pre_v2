from assembly.assembly_graph import AssemblyGraph
from manufacturing.joint_operation_generator import JointOperationGenerator

g = AssemblyGraph()

g.add_joint(
    "SIDE_PANEL",
    "TOP_PANEL",
    "MINIFIX"
)

for joint in g.all_joints():

    if joint.joint_type == "MINIFIX":

        ops = JointOperationGenerator.minifix_joint()

        print(joint)

        for op in ops:
            print("   ", op)
