from domain.builders import CabinetProject
from runtime.runtime_joinery_builder import (
    RuntimeJoineryBuilder,
)


class RuntimeProjectAdapter:

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
