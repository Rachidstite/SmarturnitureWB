from __future__ import annotations

from application.application_service_result import ApplicationServiceResult
from application.base_application_service import BaseApplicationService

# Existing components reused — no new engines, no mock fallback.
from domain.base_cabinet_engineering_entry import (
    build_base_cabinet_engineering_cabinet,
)
from domain.base_cabinet_specification import BaseCabinetSpecification
from domain.product_configuration import ProductConfiguration
from domain.product_configuration_base_cabinet_adapter import (
    adapt_product_configuration_to_base_cabinet_specification,
)


class EngineeringApplicationService(BaseApplicationService):
    """Orchestrates the engineering workflow: specification → Cabinet.

    Reuses (no duplication):
      - ``domain.base_cabinet_engineering_entry.build_base_cabinet_engineering_cabinet``
        which chains: ``BaseCabinetSpecificationAdapter.adapt`` →
        ``Cabinet.__init__`` → ``ConstructionResolver.resolve`` →
        ``BaseCabinetEngineeringModelBuilder.build`` → ``CabinetBuilder.build``

    No mock values, no REAL_ENGINE_AVAILABLE guards.
    """

    def execute_from_product_configuration(
        self,
        *,
        configuration: ProductConfiguration,
    ) -> ApplicationServiceResult:
        specification = adapt_product_configuration_to_base_cabinet_specification(
            configuration
        )
        return self.execute(specification=specification)

    def _execute(
        self,
        *,
        specification: BaseCabinetSpecification | None = None,
    ) -> ApplicationServiceResult:
        from domain.base_cabinet_specification_adapter import (
            BaseCabinetSpecificationAdapter,
        )

        spec = specification or BaseCabinetSpecification()

        # The entry point returns a real Cabinet with construction_model,
        # engineering_model, and scene_graph attached.
        cabinet = build_base_cabinet_engineering_cabinet(spec)

        adapter_result = BaseCabinetSpecificationAdapter.adapt(spec)
        metadata = dict(getattr(adapter_result, "metadata", {}) or {})

        return ApplicationServiceResult(
            success=True,
            data={
                "cabinet": cabinet,
                "specification": spec,
                "metadata": metadata,
            },
            errors=(),
            diagnostics=(),
        )
