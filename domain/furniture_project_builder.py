from domain.furniture_project import FurnitureProject


class FurnitureProjectBuilder:

    def __init__(
        self,
        project_id="",
        name="",
        cabinets=None,
        metadata=None,
    ):
        self.project_id = project_id
        self.name = name
        self._cabinets = list(cabinets) if cabinets is not None else []
        self.metadata = dict(metadata) if metadata is not None else {}

    def add_cabinet(self, cabinet):
        self._cabinets.append(cabinet)
        return self

    def add_cabinets(self, cabinets):
        self._cabinets.extend(cabinets)
        return self

    def build(self):
        return FurnitureProject(
            project_id=self.project_id,
            name=self.name,
            cabinets=list(self._cabinets),
            metadata=dict(self.metadata),
        )
