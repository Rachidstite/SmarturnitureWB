from manufacturing.machining_operation_adapter import \
    MachiningOperationAdapter


class CanonicalOperationCollector:

    @staticmethod
    def collect(scene_graph):

        operations = []

        for node in getattr(
            scene_graph,
            "physical_nodes",
            []
        ):

            for op in getattr(
                node,
                "machining_ops",
                []
            ):

                unified = (
                    MachiningOperationAdapter
                    .from_operation(op)
                )

                identity = getattr(
                    node,
                    "identity",
                    None
                )

                panel_id = getattr(
                    identity,
                    "key",
                    None
                )

                if panel_id is not None:
                    unified.metadata["panel_id"] = panel_id

                operations.append(
                    unified
                )

        return operations
