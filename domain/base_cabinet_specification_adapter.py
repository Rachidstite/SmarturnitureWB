from __future__ import annotations

from dataclasses import dataclass, field

from domain.base_cabinet_specification import BaseCabinetSpecification
from shared.contracts import CabinetParams, SectionConfig


@dataclass(frozen=True)
class BaseCabinetSpecificationAdapterResult:
    cabinet_params: CabinetParams
    metadata: dict = field(default_factory=dict)


class BaseCabinetSpecificationAdapter:
    @staticmethod
    def from_cabinet_params(
        cabinet_params: CabinetParams,
    ) -> BaseCabinetSpecification:
        section = cabinet_params.sec_data.get(0) if cabinet_params.sec_data else None
        return BaseCabinetSpecification(
            width_mm=cabinet_params.width,
            height_mm=cabinet_params.height,
            depth_mm=cabinet_params.depth,
            door_count=getattr(section, "door_count", 2),
            shelf_count=getattr(section, "shelves", 1),
            has_back_panel=True,
            edge_banding_required=True,
            toe_kick_required=cabinet_params.base_height > 0,
            hinge_family=cabinet_params.hinge_sku,
            drawer_family=getattr(section, "drawer_type", "NONE"),
        )

    @staticmethod
    def adapt(
        specification: BaseCabinetSpecification,
    ) -> BaseCabinetSpecificationAdapterResult:
        door_count = int(getattr(specification, "door_count", 0) or 0)
        shelf_count = int(getattr(specification, "shelf_count", 0) or 0)
        cabinet_params = CabinetParams(
            width=specification.width_mm,
            height=specification.height_mm,
            depth=specification.depth_mm,
            sec_count=1,
            sec_data={
                0: SectionConfig(
                    shelves=max(shelf_count, 0),
                    doors="Inset" if door_count > 0 else "None",
                    door_count=max(door_count, 0),
                )
            },
            hinge_sku=specification.hinge_family,
        )
        return BaseCabinetSpecificationAdapterResult(
            cabinet_params=cabinet_params,
            metadata={
                "door_count": specification.door_count,
                "shelf_count": specification.shelf_count,
                "has_back_panel": specification.has_back_panel,
                "edge_banding_required": specification.edge_banding_required,
                "toe_kick_required": specification.toe_kick_required,
                "hinge_family": specification.hinge_family,
                "drawer_family": specification.drawer_family,
            },
        )
