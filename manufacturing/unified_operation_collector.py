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

    @staticmethod
    def collect_legacy(scene_graph):

        operations = []

        panel_ops = (
            PanelOperationEngine
            .generate(scene_graph)
        )

        for panel_id, op_list in panel_ops.items():

            for op in op_list:

                unified = (
                    LegacyOperationAdapter
                    .from_operation(op)
                )

                unified.metadata["panel_id"] = panel_id

                operations.append(
                    unified
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
