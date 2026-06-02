from domain.manufacturing_ops import FaceDrill, EdgeDrill

class JointOperationGenerator:

    @staticmethod
    def minifix_joint():

        ops = []

        # Cam 15mm
        ops.append(
            FaceDrill(
                x=34,
                y=64,
                diameter=15,
                depth=12,
                face="TOP"
            )
        )

        # Dowel hole
        ops.append(
            EdgeDrill(
                x=64,
                z=9,
                diameter=8,
                depth=30,
                edge="TOP"
            )
        )

        return ops
