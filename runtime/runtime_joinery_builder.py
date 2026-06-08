from domain.assembly_graph import JoineryGraph
from domain.core_types import JoineryType


class RuntimeJoineryBuilder:

    @staticmethod
    def build(scene_graph):

        joinery = JoineryGraph()

        sides = []
        tops = []
        bottoms = []
        shelves = []
        dividers = []

        for node in getattr(
            scene_graph,
            "physical_nodes",
            []
        ):
            role = str(
                getattr(node, "role", "")
            ).split(".")[-1]

            if role == "SIDE_PANEL":
                sides.append(node)

            elif role == "TOP_PANEL":
                tops.append(node)

            elif role == "BOTTOM_PANEL":
                bottoms.append(node)

            elif role == "SHELF":
                shelves.append(node)

            elif role == "DIVIDER":
                dividers.append(node)

        for side in sides:

            for bottom in bottoms:

                joinery.add_connection(
                    side.identity.key,
                    bottom.identity.key,
                    JoineryType.MINIFIX_15.value,
                )

            for top in tops:

                joinery.add_connection(
                    side.identity.key,
                    top.identity.key,
                    JoineryType.MINIFIX_15.value,
                )

        for divider in dividers:

            for bottom in bottoms:

                joinery.add_connection(
                    bottom.identity.key,
                    divider.identity.key,
                    JoineryType.CONFIRMAT_50.value,
                )

            for top in tops:

                joinery.add_connection(
                    top.identity.key,
                    divider.identity.key,
                    JoineryType.CONFIRMAT_50.value,
                )

        for shelf in shelves:

            joinery.add_connection(
                "RUNTIME_SHELF_ANCHOR",
                shelf.identity.key,
                JoineryType.SHELF_PIN_5MM.value,
                "Runtime shelf support",
            )

        return joinery
