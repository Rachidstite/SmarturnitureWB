from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .interactive_components import (
    InteractiveVisualComponent,
    build_interactive_visual_components,
)
from .presentation_synchronization import (
    SynchronizedPresentation,
    synchronize_presentation,
)
from .projection_adapters import (
    build_inspector_read_model,
    build_manufacturing_review_projection,
    build_message_center_read_model,
    build_preview_read_model,
    build_project_tree_read_model,
    build_review_panel_read_models,
    build_validation_review_projection,
)
from .read_models import MessageReadModel, ReviewPanelReadModel, empty_inspector_read_model
from .scene_projection import SceneProjection, build_scene_projection
from .visual_components import VisualComponent, build_visual_components
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

    def _workspace_inspector_source(self):
        selection = getattr(self.workspace, "current_selection", None)
        if not selection:
            return None
        if (
            getattr(selection, "selection_type", "NONE") in ("", "NONE")
            and not getattr(selection, "selection_id", "")
            and not getattr(selection, "display_name", "")
            and not getattr(selection, "source_region", "")
            and not getattr(selection, "metadata", None)
        ):
            return None
        return selection

    def _workspace_preview_source(self):
        selection = getattr(self.workspace, "current_selection", None)
        source = {}
        if getattr(self.workspace, "current_product_family", None) is not None:
            source["current_family"] = self.workspace.current_product_family
        if getattr(self.workspace, "current_product", None) is not None:
            source["preview_title"] = self.workspace.current_product
        if selection and getattr(selection, "selection_id", ""):
            source["selection"] = selection
            source["highlighted_item_id"] = selection.selection_id
            source["highlighted_item_type"] = getattr(selection, "selection_type", "")
            source["preview_state"] = "Ready"
            source["viewport_message"] = (
                f"Focus on {getattr(selection, 'display_name', '') or selection.selection_id}"
            )
            source["available_representations"] = ("Customer View", "Design View")
            if getattr(selection, "source_region", ""):
                source["source_reference"] = selection.source_region
        if not source and getattr(self.workspace, "current_product_family", None) is not None:
            source["current_family"] = self.workspace.current_product_family
            source["preview_title"] = self.workspace.current_product_family
            source["preview_state"] = "Unavailable"
            source["viewport_message"] = "Preview integration not available yet"
            source["available_representations"] = ()
        return source or None

    def _scene_projection_source(self, source: Any = None):
        if source is None:
            return None
        if isinstance(source, dict):
            if source.get("scene_projection") is not None:
                return source.get("scene_projection")
            if source.get("scene_graph") is not None:
                return build_scene_projection(
                    source.get("scene_graph"),
                    selected_node_id=str(source.get("selected_node_id", "") or ""),
                    highlight_target=str(source.get("highlight_target", "") or ""),
                    representation_status=str(source.get("representation_status", "") or ""),
                    warnings=source.get("warnings", ()),
                    source_reference=str(source.get("source_reference", "") or ""),
                )
            return None
        if hasattr(source, "scene_projection"):
            scene_projection = getattr(source, "scene_projection", None)
            if scene_projection is not None:
                return scene_projection
        if hasattr(source, "scene_graph") and getattr(source, "scene_graph", None) is not None:
            return build_scene_projection(
                getattr(source, "scene_graph"),
                selected_node_id=str(getattr(source, "selected_node_id", "") or ""),
                highlight_target=str(getattr(source, "highlight_target", "") or ""),
                representation_status=str(getattr(source, "representation_status", "") or ""),
                warnings=getattr(source, "warnings", ()),
                source_reference=str(getattr(source, "source_reference", "") or ""),
            )
        if hasattr(source, "all_nodes") and callable(getattr(source, "all_nodes")):
            return build_scene_projection(source)
        return None

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

    def refresh_inspector(self, source: Any = None):
        source = source if source is not None else self._workspace_inspector_source()
        if not source:
            read_model = empty_inspector_read_model()
            self.workspace.set_inspector_read_model(read_model)
            self.push_message(
                severity="INFO",
                text="Inspector integration not available yet",
                category="Inspector integration",
                source_reference="ConfiguratorV2ServiceIntegration.refresh_inspector",
            )
            return read_model

        read_model = build_inspector_read_model(source)
        if read_model.unsupported:
            severity = "UNSUPPORTED"
            text = read_model.unsupported_reason or "Selected object is not supported yet"
            self.push_message(
                severity=severity,
                text=text,
                category="Inspector integration",
                source_reference=read_model.source_reference
                or "ConfiguratorV2ServiceIntegration.refresh_inspector",
            )
        self.workspace.set_inspector_read_model(read_model)
        return read_model

    def refresh_preview(
        self,
        source: Any = None,
        *,
        show_hardware: bool | None = None,
        show_feature_markers: bool | None = None,
        show_door_swing: bool | None = None,
        show_drawer_open: bool | None = None,
    ):
        source = source if source is not None else self._workspace_preview_source()
        if not source:
            read_model = build_preview_read_model(
                {
                    "preview_title": "Preview",
                    "preview_state": "Unavailable",
                    "viewport_message": "Preview integration not available yet",
                    "available_representations": (),
                    "warnings": (),
                    "unsupported_reason": "Preview integration not available yet",
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

        scene_projection = self._scene_projection_source(source)
        if scene_projection is not None:
            visual_components = build_visual_components(scene_projection)
            kwargs: dict[str, Any] = {}
            if show_hardware is not None:
                kwargs["show_hardware"] = show_hardware
            if show_feature_markers is not None:
                kwargs["show_feature_markers"] = show_feature_markers
            if show_door_swing is not None:
                kwargs["show_door_swing"] = show_door_swing
            if show_drawer_open is not None:
                kwargs["show_drawer_open"] = show_drawer_open
            if kwargs:
                interactive = build_interactive_visual_components(
                    visual_components, **kwargs
                )
                source = {
                    **(source if isinstance(source, dict) else {}),
                    "scene_projection": scene_projection,
                    "interactive_components": interactive,
                }
            else:
                source = {
                    **(source if isinstance(source, dict) else {}),
                    "scene_projection": scene_projection,
                    "visual_components": visual_components,
                }

        read_model = build_preview_read_model(source)
        if read_model.unsupported_reason:
            self.push_message(
                severity="UNSUPPORTED",
                text=read_model.unsupported_reason,
                category="Preview integration",
                source_reference="ConfiguratorV2ServiceIntegration.refresh_preview",
            )
        if scene_projection is not None:
            interactive_in_source = source.get("interactive_components", None) if isinstance(source, dict) else None
            if interactive_in_source is not None:
                self.workspace.set_preview_interactive_components(
                    interactive_in_source,
                    read_model,
                )
            else:
                self.workspace.set_preview_visual_components(
                    source.get("visual_components", ()),
                    read_model,
                )
        else:
            self.workspace.set_preview_read_model(read_model)
        return read_model

    def refresh_validation(self, source: Any = None):
        if source is None:
            return self._refresh_review_panels(
                source=source,
                message_text="Validation integration not available yet",
                source_reference="ConfiguratorV2ServiceIntegration.refresh_validation",
            )
        panel = build_validation_review_projection(source)
        existing = tuple(self.workspace.review_panel_read_models or ())
        names = self.workspace.review_panel_names
        merged = tuple(
            panel if name == "Validation"
            else existing[i] if i < len(existing)
            else ReviewPanelReadModel(panel_name=name)
            for i, name in enumerate(names)
        )
        self.workspace.set_review_panel_read_models(merged)
        return merged

    def refresh_manufacturing_review(self, source: Any = None):
        if source is None:
            return self._refresh_review_panels(
                source=source,
                message_text="Manufacturing review integration not available yet",
                source_reference="ConfiguratorV2ServiceIntegration.refresh_manufacturing_review",
            )
        panel = build_manufacturing_review_projection(source)
        existing = tuple(self.workspace.review_panel_read_models or ())
        names = self.workspace.review_panel_names
        merged = tuple(
            panel if name == "Manufacturing"
            else existing[i] if i < len(existing)
            else ReviewPanelReadModel(panel_name=name)
            for i, name in enumerate(names)
        )
        self.workspace.set_review_panel_read_models(merged)
        return merged

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


@dataclass(frozen=True)
class EngineeringProjectionResult:
    """Read-only result of projecting Engineering source through the adapter pipeline.

    All fields are CV2-native frozen dataclasses — no Engineering types,
    no domain types, no FreeCAD objects.

    The ``visual_components`` and ``interactive_components`` fields are
    mutually exclusive: interactive_components is populated when any
    interaction toggle (show_hardware, show_door_swing, etc.) is provided;
    otherwise visual_components is populated.
    """

    scene_projection: SceneProjection | None = None
    visual_components: tuple[VisualComponent, ...] = field(default_factory=tuple)
    interactive_components: tuple[InteractiveVisualComponent, ...] = field(
        default_factory=tuple
    )
    synchronized_states: tuple[SynchronizedPresentation, ...] = field(
        default_factory=tuple
    )

    def __post_init__(self):
        if not isinstance(self.scene_projection, (SceneProjection, type(None))):
            object.__setattr__(self, "scene_projection", None)
        if not isinstance(self.visual_components, tuple):
            object.__setattr__(self, "visual_components", ())
        if not isinstance(self.interactive_components, tuple):
            object.__setattr__(self, "interactive_components", ())
        if not isinstance(self.synchronized_states, tuple):
            object.__setattr__(self, "synchronized_states", ())


def project_engineering_source(
    source: Any,
    *,
    selected_component_id: str = "",
    highlighted_component_id: str = "",
    show_hardware: bool | None = None,
    show_feature_markers: bool | None = None,
    show_door_swing: bool | None = None,
    show_drawer_open: bool | None = None,
    selected_ids: frozenset[str] | None = None,
    hovered_id: str = "",
    focused_id: str = "",
    disabled_ids: frozenset[str] | None = None,
    warning_ids: frozenset[str] | None = None,
    error_ids: frozenset[str] | None = None,
    preview_ids: frozenset[str] | None = None,
    active_ids: frozenset[str] | None = None,
    muted_ids: frozenset[str] | None = None,
) -> EngineeringProjectionResult:
    """Project Engineering source data through the CV2 adapter pipeline.

    This is the single entry point for Engineering data into CV2.
    It composes the existing projection, visual component, interactive,
    and presentation synchronization layers without exposing any
    Engineering types to the UI.

    Parameters
    ----------
    source : Duck-typed Engineering source (SceneGraph, dict, or any
             object with ``all_nodes()``, ``nodes``, or ``children``).
    All other parameters : Standard CV2 interactive + presentation flags.

    Returns
    -------
    EngineeringProjectionResult with only CV2-native frozen dataclasses.

    The function is deterministic and side-effect free.
    """
    scene_projection = build_scene_projection(
        source,
        selected_node_id=selected_component_id,
        highlight_target=highlighted_component_id,
    )

    if scene_projection is None or not scene_projection.nodes:
        return EngineeringProjectionResult()

    visual_components = build_visual_components(scene_projection)

    has_interactive_toggles = any(
        x is not None
        for x in [show_hardware, show_feature_markers, show_door_swing, show_drawer_open]
    )

    interactive_components: tuple[InteractiveVisualComponent, ...] = ()
    synchronized_states: tuple[SynchronizedPresentation, ...] = ()

    if has_interactive_toggles:
        interactive_components = build_interactive_visual_components(
            visual_components,
            selected_component_id=selected_component_id,
            highlighted_component_id=highlighted_component_id,
            show_hardware=True if show_hardware is None else show_hardware,
            show_feature_markers=True
            if show_feature_markers is None
            else show_feature_markers,
            show_door_swing=False if show_door_swing is None else show_door_swing,
            show_drawer_open=False if show_drawer_open is None else show_drawer_open,
        )

        has_presentation_flags = any(
            x is not None
            for x in [
                selected_ids,
                hovered_id,
                focused_id,
                disabled_ids,
                warning_ids,
                error_ids,
                preview_ids,
                active_ids,
                muted_ids,
            ]
        )
        if has_presentation_flags:
            ids = tuple(ic.component_id for ic in interactive_components)
            synchronized_states = synchronize_presentation(
                ids,
                selected_ids=selected_ids,
                hovered_id=hovered_id,
                focused_id=focused_id,
                disabled_ids=disabled_ids,
                warning_ids=warning_ids,
                error_ids=error_ids,
                preview_ids=preview_ids,
                active_ids=active_ids,
                muted_ids=muted_ids,
            )

    return EngineeringProjectionResult(
        scene_projection=scene_projection,
        visual_components=visual_components if not has_interactive_toggles else (),
        interactive_components=interactive_components,
        synchronized_states=synchronized_states,
    )


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
    "EngineeringProjectionResult",
    "project_engineering_source",
]
