from domain.furniture_project import CabinetPlacement, FurnitureProject


class FurnitureProjectBuilder:

    def __init__(
        self,
        project_id="",
        name="",
        cabinets=None,
        placements=None,
        metadata=None,
    ):
        self.project_id = project_id
        self.name = name
        self._cabinets = list(cabinets) if cabinets is not None else []
        self._placements = list(placements) if placements is not None else []
        self.metadata = dict(metadata) if metadata is not None else {}

    def add_cabinet(self, cabinet):
        self._cabinets.append(cabinet)
        return self

    def add_cabinet_at(self, cabinet, x: float, y: float, z: float, rotation_z: float = 0.0):
        self._cabinets.append(cabinet)
        cabinet_id = (
            getattr(cabinet, "uid", "")
            or getattr(cabinet, "project_id", "")
            or getattr(cabinet, "id", "")
            or getattr(cabinet, "name", "")
            or ""
        )
        if not cabinet_id:
            graph = getattr(cabinet, "graph", None)
            physical_nodes = getattr(graph, "physical_nodes", None) or []
            if physical_nodes:
                first_identity = getattr(getattr(physical_nodes[0], "identity", None), "key", "")
                if first_identity:
                    cabinet_id = first_identity.split("_", 1)[0]
        self._placements.append(
            CabinetPlacement(
                cabinet_id=cabinet_id,
                x=x,
                y=y,
                z=z,
                rotation_z=rotation_z,
            )
        )
        return self

    def add_cabinets(self, cabinets):
        self._cabinets.extend(cabinets)
        return self

    def build(self):
        return FurnitureProject(
            project_id=self.project_id,
            name=self.name,
            cabinets=list(self._cabinets),
            placements=list(self._placements),
            metadata=dict(self.metadata),
        )
