from __future__ import annotations

from typing import Any

from application.application_service_result import ApplicationServiceResult
from application.base_application_service import BaseApplicationService

# Existing components reused — no new engines, no mock fallback.
from domain.base_cabinet_product_workflow import (
    build_base_cabinet_product_workflow,
)
from domain.base_cabinet_specification import BaseCabinetSpecification
from domain.product_configuration import ProductConfiguration
from domain.product_configuration_family_classifier import (
    classify_product_configuration_family,
)
from domain.product_configuration_base_cabinet_adapter import (
    adapt_product_configuration_to_base_cabinet_specification,
)
from domain.product_configuration_wall_cabinet_mapper import (
    build_wall_cabinet_specification_from_product_configuration,
)
from domain.wall_cabinet_engineering_entry import (
    build_wall_cabinet_engineering_cabinet,
)


class ProjectApplicationService(BaseApplicationService):
    """Orchestrates FreeCAD document management and the full product workflow.

    Reuses (no duplication):
      - ``services.project_service.ProjectService`` for FreeCAD document ops
      - ``domain.base_cabinet_product_workflow.build_base_cabinet_product_workflow``
        which itself chains: engineering → validation → manufacturing → cost → commercial
    """

    def execute_from_product_configuration(
        self,
        *,
        configuration: ProductConfiguration,
        quotation_metadata: dict | None = None,
        create_document: bool = True,
    ) -> ApplicationServiceResult:
        classification = classify_product_configuration_family(configuration)
        if not classification.executable_family:
            raise ValueError(
                f"family_id={classification.family_id!r} is not executable: "
                f"{classification.reason}"
            )
        if classification.engineering_path == "wall_cabinet":
            wall_specification = (
                build_wall_cabinet_specification_from_product_configuration(
                    configuration
                )
            )
            wall_result = build_wall_cabinet_engineering_cabinet(
                wall_specification
            )
            return ApplicationServiceResult(
                success=True,
                data=wall_result,
                errors=(),
                diagnostics=(),
            )
        if classification.engineering_path != "base_cabinet":
            raise ValueError(
                "Unsupported engineering path for "
                f"family_id={classification.family_id!r}: "
                f"{classification.engineering_path!r}"
            )
        specification = adapt_product_configuration_to_base_cabinet_specification(
            configuration
        )
        return self.execute(
            specification=specification,
            quotation_metadata=quotation_metadata,
            create_document=create_document,
        )

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
