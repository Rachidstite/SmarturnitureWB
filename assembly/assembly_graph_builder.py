from assembly.assembly_graph import AssemblyGraph
from shared.roles import NodeRole

class AssemblyGraphBuilder:

    @staticmethod
    def build(scene_graph):

        g = AssemblyGraph()

        nodes = scene_graph.all_nodes()

        sides = [
            n for n in nodes
            if n.role == NodeRole.SIDE_PANEL
        ]

        tops = [
            n for n in nodes
            if n.role == NodeRole.TOP_PANEL
        ]

        bottoms = [
            n for n in nodes
            if n.role == NodeRole.BOTTOM_PANEL
        ]

        dividers = [
            n for n in nodes
            if n.role == NodeRole.DIVIDER
        ]

        doors = [
            n for n in nodes
            if n.role == NodeRole.DOOR_PANEL
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
