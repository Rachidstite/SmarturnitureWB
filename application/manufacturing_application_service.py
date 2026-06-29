from __future__ import annotations

from application.application_service_result import ApplicationServiceResult
from application.base_application_service import BaseApplicationService

# Existing components reused — no new engines, no mock fallback.
from domain.base_cabinet_manufacturing_outputs_entry import (
    BaseCabinetManufacturingOutputsEntryResult,
    build_base_cabinet_manufacturing_outputs_entry,
)
from domain.base_cabinet_specification import BaseCabinetSpecification


class ManufacturingApplicationService(BaseApplicationService):
    """Orchestrates the manufacturing-outputs pipeline.

    Reuses (no duplication):
      - ``domain.base_cabinet_manufacturing_outputs_entry
        .build_base_cabinet_manufacturing_outputs_entry``
        which chains: engineering entry → scene graph →
        ``ManufacturingRuntimePipelineBuilder`` →
        ``ManufacturingCutlistBuilder``

    No mock values, no REAL_ENGINE_AVAILABLE guards.
    """

    def _execute(
        self,
        *,
        specification: BaseCabinetSpecification | None = None,
    ) -> ApplicationServiceResult:
        spec = specification or BaseCabinetSpecification()

        entry_result: BaseCabinetManufacturingOutputsEntryResult = (
            build_base_cabinet_manufacturing_outputs_entry(spec)
        )

        return ApplicationServiceResult(
            success=True,
            data={
                "manufacturing_outputs": entry_result,
                "cut_list": entry_result.cut_list,
                "manufacturing_package": entry_result.manufacturing_package,
                "metadata": entry_result.metadata,
                "specification": spec,
            },
            errors=(),
            diagnostics=(),
        )
