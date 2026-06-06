from manufacturing.machining_operation_adapter import \
    MachiningOperationAdapter

from manufacturing.legacy_operation_adapter import \
    LegacyOperationAdapter

from manufacturing.panel_operation_engine import \
    PanelOperationEngine


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

    @staticmethod
    def collect_legacy(scene_graph):

        operations = []

        panel_ops = (
            PanelOperationEngine
            .generate(scene_graph)
        )

        for op_list in panel_ops.values():

            for op in op_list:

                operations.append(
                    LegacyOperationAdapter
                    .from_operation(op)
                )

        return operations


    @staticmethod
    def collect_hybrid(scene_graph):

        return (
            UnifiedOperationCollector
            .collect_legacy(scene_graph)
            +
            UnifiedOperationCollector
            .collect_modern(scene_graph)
        )
