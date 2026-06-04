from types import SimpleNamespace

from assembly.assembly_graph import AssemblyGraph
from manufacturing.joint_operation_generator import JointOperationGenerator

g = AssemblyGraph()

g.add_joint(
    "SIDE_PANEL",
    "TOP_PANEL",
    "MINIFIX"
)

parent_node = SimpleNamespace(
    thickness=18.0,
    width=600,
    depth=500,
    height=720
)

child_node = SimpleNamespace(
    thickness=18.0,
    width=564,
    depth=500,
    height=18
)

for joint in g.all_joints():

    if joint.joint_type == "MINIFIX":

        ops = JointOperationGenerator.minifix_joint(
            parent_node,
            child_node
        )

        print(joint)

        for op in ops:
            print("   ", op)
