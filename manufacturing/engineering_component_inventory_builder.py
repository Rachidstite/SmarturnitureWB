from manufacturing.engineering_component_inventory import (
    BackPanelRecord,
    CabinetRecord,
    ComponentProvenance,
    DoorRecord,
    EngineeringComponentInventory,
    ShelfRecord,
)
from domain.core_types import NodeRole


class EngineeringComponentInventoryBuilder:

    def build(self, project):
        if hasattr(project, "cabinets"):
            return self._build_furniture_project(project)
        return self._build_project_inventory(project)

    def _build_furniture_project(self, furniture_project):
        cabinet_records = []
        door_records = []
        shelf_records = []
        back_panel_records = []
        warnings = list(getattr(furniture_project, "warnings", []) or [])

        cabinets = list(getattr(furniture_project, "cabinets", []) or [])
        for index, cabinet in enumerate(cabinets):
            cabinet_scope = f"FurnitureProject.cabinets[{index}]"
            scene_graph = getattr(cabinet, "graph", cabinet)
            topology = getattr(cabinet, "topology", None)
            cabinet_source_path = self._cabinet_source_path(
                cabinet_scope,
                topology,
                has_graph=scene_graph is not cabinet or hasattr(cabinet, "graph"),
            )
            node_source_path = self._node_source_path(
                cabinet_scope,
                has_graph=scene_graph is not cabinet or hasattr(cabinet, "graph"),
            )

            cabinet_records.append(
                self._build_cabinet_record(
                    cabinet,
                    topology,
                    cabinet_source_path,
                )
            )
            self._collect_component_records(
                scene_graph,
                node_source_path,
                door_records,
                shelf_records,
                back_panel_records,
            )

        warnings.extend(
            self._collect_record_warnings(
                cabinet_records,
                door_records,
                shelf_records,
                back_panel_records,
            )
        )

        return EngineeringComponentInventory(
            cabinet_records=cabinet_records,
            door_records=door_records,
            shelf_records=shelf_records,
            back_panel_records=back_panel_records,
            warnings=warnings,
        )

    def _build_project_inventory(self, cabinet_project):
        scene_graph = getattr(cabinet_project, "graph", cabinet_project)
        physical_nodes = list(getattr(scene_graph, "physical_nodes", []) or [])
        topology = getattr(cabinet_project, "topology", None)
        cabinet_source_path = (
            "CabinetProject.topology"
            if topology is not None
            else "SceneGraph.physical_nodes"
        )
        node_source_path = (
            "CabinetProject.graph.physical_nodes"
            if topology is not None
            else "SceneGraph.physical_nodes"
        )

        cabinet_records = [
            self._build_cabinet_record(
                cabinet_project,
                topology,
                cabinet_source_path,
            )
        ]
        door_records = []
        shelf_records = []
        back_panel_records = []
        warnings = list(getattr(cabinet_project, "warnings", []) or [])

        self._collect_component_records(
            scene_graph,
            node_source_path,
            door_records,
            shelf_records,
            back_panel_records,
        )

        warnings.extend(
            self._collect_record_warnings(
                cabinet_records,
                door_records,
                shelf_records,
                back_panel_records,
            )
        )

        return EngineeringComponentInventory(
            cabinet_records=cabinet_records,
            door_records=door_records,
            shelf_records=shelf_records,
            back_panel_records=back_panel_records,
            warnings=warnings,
        )

    def _collect_component_records(
        self,
        scene_graph,
        source_path,
        door_records,
        shelf_records,
        back_panel_records,
    ):
        physical_nodes = list(getattr(scene_graph, "physical_nodes", []) or [])
        for node in physical_nodes:
            role = getattr(node, "role", NodeRole.UNKNOWN)
            if role == NodeRole.DOOR_PANEL:
                door_records.append(
                    self._build_door_record(node, source_path)
                )
            elif role == NodeRole.SHELF:
                shelf_records.append(
                    self._build_shelf_record(node, source_path)
                )
            elif role == NodeRole.BACK_PANEL:
                back_panel_records.append(
                    self._build_back_panel_record(node, source_path)
                )

    @staticmethod
    def _cabinet_source_path(cabinet_scope, topology, has_graph):
        if topology is not None:
            return f"{cabinet_scope}.topology"
        if has_graph:
            return f"{cabinet_scope}.graph.physical_nodes"
        return f"{cabinet_scope}.physical_nodes"

    @staticmethod
    def _node_source_path(cabinet_scope, has_graph):
        if has_graph:
            return f"{cabinet_scope}.graph.physical_nodes"
        return f"{cabinet_scope}.physical_nodes"

    def _build_cabinet_record(self, cabinet_project, topology, source_path):
        cabinet_id = self._cabinet_id(cabinet_project)
        source_object_id = cabinet_id
        provenance = ComponentProvenance(
            source_system="EngineeringComponentInventoryBuilder",
            source_object_type=type(cabinet_project).__name__,
            source_object_id=source_object_id,
            source_role="CABINET_PROJECT",
            source_path=source_path,
            derivation_mode="inferred",
            confidence_level="MEDIUM",
            notes="Normalized from cabinet project boundary.",
        )

        width = float(getattr(topology, "w", 0.0) or 0.0)
        height = float(getattr(topology, "h", 0.0) or 0.0)
        depth = float(getattr(topology, "d", 0.0) or 0.0)
        thickness = float(getattr(topology, "t", 0.0) or 0.0)

        warnings = []
        if width <= 0 or height <= 0:
            warnings.append("Cabinet topology is incomplete")

        return CabinetRecord(
            cabinet_id=cabinet_id,
            provenance=provenance,
            width=width,
            height=height,
            depth=depth,
            thickness=thickness,
            material="",
            warnings=warnings,
        )

    @staticmethod
    def _cabinet_id(cabinet_project):
        cabinet_id = getattr(cabinet_project, "cabinet_id", "")
        if cabinet_id:
            return str(cabinet_id)
        identity = getattr(cabinet_project, "identity", None)
        return str(getattr(identity, "key", "") or "")

    def _build_door_record(self, node, source_path):
        return DoorRecord(
            provenance=self._node_provenance(
                node,
                source_role="DOOR_PANEL",
                source_path=source_path,
                confidence_level="HIGH",
                notes="Normalized from a door panel scene node.",
            ),
            width=float(getattr(node, "width", 0.0) or 0.0),
            height=float(getattr(node, "height", 0.0) or 0.0),
            thickness=float(getattr(node, "thickness", 0.0) or 0.0),
            material=str(getattr(node, "material", "") or ""),
            warnings=list(getattr(node, "warnings", []) or []),
        )

    def _build_shelf_record(self, node, source_path):
        return ShelfRecord(
            provenance=self._node_provenance(
                node,
                source_role="SHELF",
                source_path=source_path,
                confidence_level="HIGH",
                notes="Normalized from a shelf scene node.",
            ),
            width=float(getattr(node, "width", 0.0) or 0.0),
            height=float(getattr(node, "height", 0.0) or 0.0),
            thickness=float(getattr(node, "thickness", 0.0) or 0.0),
            material=str(getattr(node, "material", "") or ""),
            warnings=list(getattr(node, "warnings", []) or []),
        )

    def _build_back_panel_record(self, node, source_path):
        return BackPanelRecord(
            provenance=self._node_provenance(
                node,
                source_role="BACK_PANEL",
                source_path=source_path,
                confidence_level="HIGH",
                notes="Normalized from a back panel scene node.",
            ),
            width=float(getattr(node, "width", 0.0) or 0.0),
            height=float(getattr(node, "height", 0.0) or 0.0),
            thickness=float(getattr(node, "thickness", 0.0) or 0.0),
            material=str(getattr(node, "material", "") or ""),
            warnings=list(getattr(node, "warnings", []) or []),
        )

    def _node_provenance(
        self,
        node,
        *,
        source_role,
        source_path,
        confidence_level,
        notes,
    ):
        identity = getattr(node, "identity", None)
        source_object_id = str(getattr(identity, "key", "") or "")
        return ComponentProvenance(
            source_system="EngineeringComponentInventoryBuilder",
            source_object_type=type(node).__name__,
            source_object_id=source_object_id,
            source_role=source_role,
            source_path=source_path,
            derivation_mode="direct",
            confidence_level=confidence_level,
            notes=notes,
        )

    @staticmethod
    def _collect_record_warnings(*record_groups):
        warnings = []
        for group in record_groups:
            for record in group:
                warnings.extend(list(getattr(record, "warnings", []) or []))
        unique_warnings = []
        for warning in warnings:
            if warning not in unique_warnings:
                unique_warnings.append(warning)
        return unique_warnings
