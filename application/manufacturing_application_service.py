from __future__ import annotations

from application.application_service_result import ApplicationServiceResult
from application.base_application_service import BaseApplicationService

# Existing components reused — no new engines, no mock fallback.
from domain.base_cabinet_manufacturing_outputs_entry import (
    BaseCabinetManufacturingOutputsEntryResult,
    build_base_cabinet_manufacturing_outputs_entry,
)
from domain.base_cabinet_specification import BaseCabinetSpecification
from manufacturing.factory_release_package import FactoryReleasePackage
from manufacturing.manufacturing_decision_builder import ManufacturingDecisionBuilder
from manufacturing.manufacturing_production_package_builder import (
    ManufacturingProductionPackageBuilder,
)


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
        manufacturing_production_package = ManufacturingProductionPackageBuilder().build(
            entry_result.manufacturing_package
        )
        manufacturing_decision = ManufacturingDecisionBuilder().build(
            production_evidence=manufacturing_production_package.production_evidence
        )
        factory_release_package = FactoryReleasePackage(
            manufacturing_decision=manufacturing_decision,
            cut_list=entry_result.cut_list,
            hardware_bom=manufacturing_production_package.hardware_report,
            cnc_package=manufacturing_production_package.cnc_report,
            assembly_package=manufacturing_production_package.assembly_report,
            warnings=manufacturing_production_package.warnings,
            metadata=entry_result.metadata,
        )

        return ApplicationServiceResult(
            success=True,
            data={
                "manufacturing_outputs": entry_result,
                "cut_list": entry_result.cut_list,
                "manufacturing_package": entry_result.manufacturing_package,
                "manufacturing_production_package": manufacturing_production_package,
                "manufacturing_decision": manufacturing_decision,
                "factory_release_package": factory_release_package,
                "metadata": entry_result.metadata,
                "specification": spec,
            },
            errors=(),
            diagnostics=(),
        )
