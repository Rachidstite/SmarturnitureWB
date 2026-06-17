from domain.anchors import MountFace
from domain.manufacturing_ops import EdgeDrill, FaceDrill


class HardwareOperationAdapter:

    @staticmethod
    def to_unified(hole_specs, anchor=None, target_kind=None):
        operations = []

        for hole in list(hole_specs or []):
            face = hole.face.value if hasattr(hole.face, "value") else hole.face

            if hole.axis == "X" or face in ("LEFT", "RIGHT"):
                operations.append(
                    EdgeDrill(
                        x=hole.offset_x,
                        z=hole.offset_y,
                        diameter=hole.diameter,
                        depth=hole.depth,
                        edge=face,
                    )
                )
            else:
                operations.append(
                    FaceDrill(
                        x=hole.offset_x,
                        y=hole.offset_y,
                        diameter=hole.diameter,
                        depth=hole.depth,
                        face=face,
                    )
                )

        return operations
