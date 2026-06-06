from assembly.assembly_graph import AssemblyGraph
from shared.roles import NodeRole

class AssemblyGraphBuilder:

    @staticmethod
    def build(scene_graph):

        g = AssemblyGraph()

        nodes = scene_graph.all_nodes()

        sides = [
            n for n in nodes
            if getattr(n.role, "name", str(n.role).split(".")[-1]) == "SIDE_PANEL"
        ]

        tops = [
            n for n in nodes
            if getattr(n.role, "name", str(n.role).split(".")[-1]) == "TOP_PANEL"
        ]

        bottoms = [
            n for n in nodes
            if getattr(n.role, "name", str(n.role).split(".")[-1]) == "BOTTOM_PANEL"
        ]

        dividers = [
            n for n in nodes
            if getattr(n.role, "name", str(n.role).split(".")[-1]) == "DIVIDER"
        ]

        doors = [
            n for n in nodes
            if getattr(n.role, "name", str(n.role).split(".")[-1]) == "DOOR_PANEL"
        ]

        for side in sides:
            for top in tops:
                g.add_joint(
                    side.identity.key,
                    top.identity.key,
                    "MINIFIX"
                )

            for bottom in bottoms:
                g.add_joint(
                    side.identity.key,
                    bottom.identity.key,
                    "MINIFIX"
                )

        for div in dividers:
            for top in tops:
                g.add_joint(
                    div.identity.key,
                    top.identity.key,
                    "MINIFIX"
                )

            for bottom in bottoms:
                g.add_joint(
                    div.identity.key,
                    bottom.identity.key,
                    "MINIFIX"
                )

        for door in doors:
            g.add_joint(
                door.identity.key,
                "CABINET",
                "HINGE"
            )

        return g
