from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .projection_adapters import (
    build_message_center_read_model,
    build_preview_read_model,
    build_project_tree_read_model,
    build_review_panel_read_models,
)
from .read_models import MessageReadModel
from .workspace import (
    ConfiguratorV2ServiceBindings,
    ConfiguratorV2Workspace,
    empty_project_tree_read_model,
    empty_review_panel_read_models,
)


@dataclass
class ConfiguratorV2ServiceIntegration:
    workspace: ConfiguratorV2Workspace
    service_bindings: ConfiguratorV2ServiceBindings | None = None

    def __post_init__(self):
        self.service_bindings = self.service_bindings or ConfiguratorV2ServiceBindings()

    def push_message(
        self,
        *,
        severity: str,
        text: str,
        category: str = "Integration",
        source_reference: str = "",
        acknowledged: bool = False,
        blocking: bool = False,
    ):
        existing_messages = tuple(self.workspace.message_center_read_model.messages or ())
        next_message = MessageReadModel(
            message_id=f"integration-{len(existing_messages) + 1}",
            severity=severity,
            category=category,
            text=text,
            source_reference=source_reference,
            acknowledged=acknowledged,
            blocking=blocking,
        )
        read_model = build_message_center_read_model(
            {"messages": existing_messages + (next_message,)}
        )
        self.workspace.set_message_center_read_model(read_model)
        return read_model

    def _workspace_project_source(self):
        source = {}
        if getattr(self.workspace, "current_customer", None) is not None:
            source["customer"] = self.workspace.current_customer
        if getattr(self.workspace, "current_project", None) is not None:
            source["project"] = self.workspace.current_project
        if getattr(self.workspace, "current_product_family", None) is not None:
            source["product"] = self.workspace.current_product_family
        if getattr(self.workspace, "current_product", None) is not None:
            source["cabinet"] = self.workspace.current_product
        selection = getattr(self.workspace, "current_selection", None)
        if selection and getattr(selection, "selection_id", ""):
            source["selected_node_id"] = selection.selection_id
        return source or None

    def refresh_project_tree(self, source: Any = None):
        source = source if source is not None else self._workspace_project_source()
        if not source:
            read_model = empty_project_tree_read_model()
            self.workspace.set_project_tree_read_model(read_model)
            self.push_message(
                severity="INFO",
                text="Project service integration not available yet",
                category="Project integration",
                source_reference="ConfiguratorV2ServiceIntegration.refresh_project_tree",
            )
            return read_model

        read_model = build_project_tree_read_model(source)
        self.workspace.set_project_tree_read_model(read_model)
        return read_model

    def refresh_preview(self, source: Any = None):
        if source is None:
            selection = getattr(self.workspace, "current_selection", None)
            highlighted_item_id = getattr(selection, "selection_id", "") if selection else ""
            read_model = build_preview_read_model(
                {
                    "highlighted_item_id": highlighted_item_id,
                    "unsupported_reason": "Preview integration not available yet",
                    "items": (),
                },
                stale=False,
            )
            self.workspace.set_preview_read_model(read_model)
            self.push_message(
                severity="UNSUPPORTED",
                text="Preview integration not available yet",
                category="Preview integration",
                source_reference="ConfiguratorV2ServiceIntegration.refresh_preview",
            )
            return read_model

        read_model = build_preview_read_model(source)
        self.workspace.set_preview_read_model(read_model)
        return read_model

    def refresh_validation(self, source: Any = None):
        return self._refresh_review_panels(
            source=source,
            message_text="Validation integration not available yet",
            source_reference="ConfiguratorV2ServiceIntegration.refresh_validation",
        )

    def refresh_manufacturing_review(self, source: Any = None):
        return self._refresh_review_panels(
            source=source,
            message_text="Manufacturing review integration not available yet",
            source_reference="ConfiguratorV2ServiceIntegration.refresh_manufacturing_review",
        )

    def refresh_cost_review(self, source: Any = None):
        return self._refresh_review_panels(
            source=source,
            message_text="Cost review integration not available yet",
            source_reference="ConfiguratorV2ServiceIntegration.refresh_cost_review",
        )

    def refresh_commercial_review(self, source: Any = None):
        return self._refresh_review_panels(
            source=source,
            message_text="Commercial review integration not available yet",
            source_reference="ConfiguratorV2ServiceIntegration.refresh_commercial_review",
        )

    def refresh_release_review(self, source: Any = None):
        return self._refresh_review_panels(
            source=source,
            message_text="Release integration not available yet",
            source_reference="ConfiguratorV2ServiceIntegration.refresh_release_review",
        )

    def _refresh_review_panels(
        self,
        *,
        source: Any = None,
        message_text: str,
        source_reference: str,
    ):
        if source is None:
            read_models = empty_review_panel_read_models(self.workspace.review_panel_names)
            self.workspace.set_review_panel_read_models(read_models)
            self.push_message(
                severity="INFO",
                text=message_text,
                category="Review integration",
                source_reference=source_reference,
            )
            return read_models

        read_models = build_review_panel_read_models(source, panel_names=self.workspace.review_panel_names)
        self.workspace.set_review_panel_read_models(read_models)
        return read_models


def attach_service_integration(
    workspace: ConfiguratorV2Workspace,
    service_bindings: ConfiguratorV2ServiceBindings | None = None,
) -> ConfiguratorV2ServiceIntegration:
    integration = ConfiguratorV2ServiceIntegration(
        workspace=workspace,
        service_bindings=service_bindings,
    )
    workspace.attach_service_integration(integration)
    return integration


__all__ = [
    "ConfiguratorV2ServiceIntegration",
    "attach_service_integration",
]
