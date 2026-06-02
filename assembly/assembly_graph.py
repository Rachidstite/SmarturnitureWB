from dataclasses import dataclass
from typing import List

@dataclass
class AssemblyJoint:
    parent: str
    child: str
    joint_type: str

class AssemblyGraph:

    def __init__(self):
        self.joints: List[AssemblyJoint] = []

    def add_joint(self, parent, child, joint_type):
        self.joints.append(
            AssemblyJoint(
                parent=parent,
                child=child,
                joint_type=joint_type
            )
        )

    def all_joints(self):
        return self.joints
