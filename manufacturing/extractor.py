from manufacturing.panel_spec import PanelSpec
from shared.roles import NodeRole


class ManufacturingExtractor:

    @staticmethod
    def _manufacturing_face_size(node):

        role = getattr(node, "role", None)

        # الألواح العمودية
        if role in (
            NodeRole.SIDE_PANEL,
            NodeRole.DIVIDER,
            NodeRole.PLINTH,
        ):
            return (
                getattr(node, "depth", 0.0),
                getattr(node, "height", 0.0),
            )

        if role in (
            NodeRole.DOOR_PANEL,
            NodeRole.DRAWER_FACE,
        ):
            return (
                getattr(node, "width", 0.0),
                getattr(node, "height", 0.0),
            )

        # الألواح الأفقية
        if role in (
            NodeRole.TOP_PANEL,
            NodeRole.BOTTOM_PANEL,
            NodeRole.SHELF,
        ):
            return (
                getattr(node, "width", 0.0),
                getattr(node, "depth", 0.0),
            )

        # الظهر
        if role == NodeRole.BACK_PANEL:
            return (
                getattr(node, "width", 0.0),
                getattr(node, "height", 0.0),
            )

        return (
            getattr(node, "width", 0.0),
            getattr(node, "height", 0.0),
        )

    @staticmethod
    def extract(scene_graph):

        specs = []

        for node in scene_graph.physical_nodes:

            face_width, face_height = (
                ManufacturingExtractor
                ._manufacturing_face_size(node)
            )

            spec = PanelSpec(
                identity=node.identity.key,
                role=node.role,
                width=face_width,
                height=face_height,
                thickness=node.thickness,
                material=node.material,
                span=(
                    getattr(
                        getattr(
                            node,
                            "metadata",
                            None
                        ),
                        "get",
                        lambda *a: face_width
                    )(
                        "span",
                        face_width
                    )
                    if isinstance(
                        getattr(
                            node,
                            "metadata",
                            None
                        ),
                        dict
                    )
                    else face_width
                ),
                edge_spec=getattr(
                    node,
                    "edge_spec",
                    None
                )
            )

            specs.append(spec)

        return specs
