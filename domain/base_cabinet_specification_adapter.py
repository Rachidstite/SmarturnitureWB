from __future__ import annotations

from dataclasses import dataclass, field

from domain.base_cabinet_specification import BaseCabinetSpecification
from shared.contracts import CabinetParams


@dataclass(frozen=True)
class BaseCabinetSpecificationAdapterResult:
    cabinet_params: CabinetParams
    metadata: dict = field(default_factory=dict)


class BaseCabinetSpecificationAdapter:
    @staticmethod
    def adapt(
        specification: BaseCabinetSpecification,
    ) -> BaseCabinetSpecificationAdapterResult:
        cabinet_params = CabinetParams(
            width=specification.width_mm,
            height=specification.height_mm,
            depth=specification.depth_mm,
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
