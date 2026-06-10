from domain.builders import CabinetProject
from runtime.runtime_joinery_builder import (
    RuntimeJoineryBuilder,
)


class RuntimeProjectAdapter:
    """
    Strategic runtime adapter.

    Converts an already-built SceneGraph into the current architectural
    aggregate root: CabinetProject.

    This adapter is intentionally lightweight:
    - It preserves the existing CabinetProject contract.
    - It does not introduce a new aggregate.
    - It allows runtime/generated SceneGraph instances to enter the
      manufacturing intelligence pipeline.
    """

    @staticmethod
    def from_scene_graph(scene_graph):

        return CabinetProject(
            graph=scene_graph,
            joinery=RuntimeJoineryBuilder.build(
                scene_graph
            ),
            topology=None,
            placements=[],
        )
