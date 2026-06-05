from manufacturing.machining_operation_adapter import \
    MachiningOperationAdapter


class UnifiedOperationCollector:

    @staticmethod
    def collect_modern(scene_graph):

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

                operations.append(
                    MachiningOperationAdapter
                    .from_operation(op)
                )

        return operations
