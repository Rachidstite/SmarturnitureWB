from __future__ import annotations

from typing import Any

from application.application_service_result import ApplicationServiceResult
from application.base_application_service import BaseApplicationService

# Existing components reused — no new engines, no mock fallback.
from domain.base_cabinet_product_workflow import (
    build_base_cabinet_product_workflow,
)
from domain.base_cabinet_specification import BaseCabinetSpecification


class ProjectApplicationService(BaseApplicationService):
    """Orchestrates FreeCAD document management and the full product workflow.

    Reuses (no duplication):
      - ``services.project_service.ProjectService`` for FreeCAD document ops
      - ``domain.base_cabinet_product_workflow.build_base_cabinet_product_workflow``
        which itself chains: engineering → validation → manufacturing → cost → commercial
    """

    def _execute(
        self,
        *,
        specification: BaseCabinetSpecification | None = None,
        quotation_metadata: dict[str, Any] | None = None,
        create_document: bool = True,
    ) -> ApplicationServiceResult:
        if create_document:
            # Lazy import — ProjectService depends on FreeCAD (external framework).
            from services.project_service import ProjectService

            doc = ProjectService.get_or_create_document()
            document_name = getattr(doc, "Name", str(doc))
        else:
            document_name = None

        spec = specification or BaseCabinetSpecification()
        result = build_base_cabinet_product_workflow(
            spec,
            quotation_metadata=quotation_metadata,
        )

        diagnostics = tuple(getattr(result, "diagnostics", ()) or ())

        return ApplicationServiceResult(
            success=True,
            data={
                "project_result": result,
                "document_name": document_name,
                "specification": spec,
            },
            errors=(),
            diagnostics=diagnostics,
        )
