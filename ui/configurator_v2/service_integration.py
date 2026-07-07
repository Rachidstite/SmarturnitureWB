from __future__ import annotations

import copy
import importlib
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
    build_commercial_review_projection,
    build_cost_review_projection,
    build_inspector_read_model,
    build_manufacturing_render_review_section,
    build_manufacturing_review_projection,
    build_message_center_read_model,
    build_preview_read_model,
    build_project_tree_read_model,
    build_release_review_projection,
    build_review_panel_read_models,
    build_validation_review_projection,
    enrich_inspector_source_with_specification,
)
from .foi_presentation_adapter import build_foi_presentation_read_model
from .engineering_state import ActiveEngineeringState
from factory_dashboard import build_factory_dashboard_read_model
from factory_dashboard import build_nesting_savings_dashboard_section
from factory_operational_intelligence import (
    build_factory_readiness_read_model,
    build_factory_blocking_analysis_read_model,
    build_factory_action_recommendation_read_model,
    build_production_decision_read_model,
)
from .read_models import MessageReadModel, ReviewPanelReadModel, empty_inspector_read_model
from .scene_projection import SceneProjection, build_scene_projection
from .visual_components import VisualComponent, build_visual_components
from .workspace import (
    ConfiguratorV2ServiceBindings,
    ConfiguratorSelection,
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

    @staticmethod
    def _load_attr(package_name: str, module_name: str, attr_name: str) -> Any:
        module = importlib.import_module(".".join((package_name, module_name)))
        return getattr(module, attr_name)

    def _resolve_builder_class(
        self,
        binding_name: str,
        *,
        package_name: str,
        module_name: str,
        class_name: str,
    ) -> Any:
        injected = getattr(self.service_bindings, binding_name, None)
        if injected is not None:
            return injected
        return self._load_attr(package_name, module_name, class_name)

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

        # Enrich with ActiveEngineeringState specification if available
        active_state = getattr(self.workspace, "active_engineering_state", None)
        if active_state is not None and getattr(active_state, "specification", None) is not None:
            source = enrich_inspector_source_with_specification(source, active_state)

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

    def create_base_cabinet(self):
        """Create a base cabinet through the engineering application service.

        This is a narrow UI orchestration path only:
        service call -> engineering result -> existing preview projection.
        No engineering logic, scene construction, or rendering is performed here.
        """
        service = getattr(self.service_bindings, "engineering_application_service", None)
        if service is None:
            self.push_message(
                severity="UNSUPPORTED",
                text="Engineering service integration not available yet",
                category="Engineering integration",
                source_reference="ConfiguratorV2ServiceIntegration.create_base_cabinet",
            )
            return build_preview_read_model(
                {
                    "preview_title": "Base Cabinet",
                    "preview_state": "Unavailable",
                    "viewport_message": "Engineering service integration not available yet",
                    "available_representations": (),
                    "warnings": (),
                    "unsupported_reason": "Engineering service integration not available yet",
                    "current_family": "Base Cabinet",
                },
                stale=False,
            )

        result = service.execute()
        if not result:
            error_text = "; ".join(tuple(getattr(result, "errors", ()) or ())) or (
                "Engineering service failed"
            )
            self.push_message(
                severity="WARNING",
                text=error_text,
                category="Engineering integration",
                source_reference="ConfiguratorV2ServiceIntegration.create_base_cabinet",
            )
            return build_preview_read_model(
                {
                    "preview_title": "Base Cabinet",
                    "preview_state": "Unavailable",
                    "viewport_message": error_text,
                    "available_representations": (),
                    "warnings": (),
                    "unsupported_reason": error_text,
                    "current_family": "Base Cabinet",
                },
                stale=False,
            )

        payload = getattr(result, "data", None) or {}
        cabinet = payload.get("cabinet") if isinstance(payload, dict) else None
        specification = payload.get("specification") if isinstance(payload, dict) else None
        metadata = payload.get("metadata") if isinstance(payload, dict) else {}
        scene_graph = getattr(cabinet, "scene_graph", None) or getattr(cabinet, "graph", None)

        self.workspace.active_engineering_state = ActiveEngineeringState(
            family="Base Cabinet",
            specification=specification,
            cabinet=cabinet,
            scene_graph=scene_graph,
            metadata=dict(metadata) if isinstance(metadata, dict) else {},
            engineering_dirty=False,
            manufacturing_stale=True,
            cost_stale=True,
            commercial_stale=True,
        )
        self.workspace.current_selection = ConfiguratorSelection(
            selection_type="CABINET",
            selection_id="base-cabinet",
            display_name="Base Cabinet",
            source_region="EngineeringApplicationService.execute",
            metadata={},
        )

        self.workspace.set_project_context(
            current_product_family="Base Cabinet",
            current_product="Base Cabinet",
            current_state=self.workspace.current_product_state,
        )

        preview_source = {
            "scene_graph": scene_graph,
            "preview_title": "Base Cabinet",
            "current_family": "Base Cabinet",
            "preview_state": "Ready" if scene_graph is not None else "Unavailable",
            "viewport_message": "Base cabinet engineering model ready"
            if scene_graph is not None
            else "Engineering model did not produce a scene graph",
            "available_representations": ("Customer View", "Design View")
            if scene_graph is not None
            else (),
            "warnings": tuple(getattr(result, "diagnostics", ()) or ()),
            "source_reference": "EngineeringApplicationService.execute",
        }
        if specification is not None:
            preview_source["selection"] = {
                "selection_type": "CABINET",
                "selection_id": "base-cabinet",
                "display_name": "Base Cabinet",
                "metadata": {
                    "width_mm": getattr(specification, "width_mm", ""),
                    "height_mm": getattr(specification, "height_mm", ""),
                    "depth_mm": getattr(specification, "depth_mm", ""),
                    **(metadata if isinstance(metadata, dict) else {}),
                },
            }

        preview = self.refresh_preview(preview_source)
        self.refresh_inspector()
        self.push_message(
            severity="INFO",
            text="Base cabinet created",
            category="Engineering integration",
            source_reference="ConfiguratorV2ServiceIntegration.create_base_cabinet",
        )
        return preview

    _ALLOWED_EDITABLE_FIELDS = frozenset({
        "width_mm", "height_mm", "depth_mm", "shelf_count", "door_count",
    })

    _INTEGER_FIELDS = frozenset({"shelf_count", "door_count"})

    def _update_active_base_cabinet_dimension(self, field_name: str, value: float):
        """Regenerate the active base cabinet by updating a single editable field.

        *field_name* must be one of the allowed editable fields (width_mm,
        height_mm, depth_mm, shelf_count).  Invalid field names return the
        current preview read model immediately.

        Integer-valued fields (shelf_count) are validated to be non-negative
        integers.  Invalid integer values are rejected safely.

        This helper copies the current specification, sets only the target
        field on the copy, calls ``engineering_application_service.execute``,
        updates the ``ActiveEngineeringState``, and refreshes the preview.

        Internal use only — never mutates the current specification.
        """
        if field_name not in self._ALLOWED_EDITABLE_FIELDS:
            self.push_message(
                severity="WARNING",
                text=f"Invalid editable field: {field_name}",
                category="Engineering integration",
                source_reference=(
                    "ConfiguratorV2ServiceIntegration._update_active_base_cabinet_dimension"
                ),
            )
            return self.workspace.preview_read_model

        # Integer field validation
        if field_name in self._INTEGER_FIELDS:
            if not isinstance(value, int) or value < 0:
                self.push_message(
                    severity="WARNING",
                    text=f"Invalid value for {field_name}: must be a non-negative integer",
                    category="Engineering integration",
                    source_reference=(
                        "ConfiguratorV2ServiceIntegration._update_active_base_cabinet_dimension"
                    ),
                )
                return self.workspace.preview_read_model

        service = getattr(self.service_bindings, "engineering_application_service", None)
        if service is None:
            self.push_message(
                severity="UNSUPPORTED",
                text="Engineering service integration not available yet",
                category="Engineering integration",
                source_reference=(
                    "ConfiguratorV2ServiceIntegration._update_active_base_cabinet_dimension"
                ),
            )
            return self.workspace.preview_read_model

        active_state = getattr(self.workspace, "active_engineering_state", None)
        current_specification = getattr(active_state, "specification", None)
        if current_specification is None:
            self.push_message(
                severity="WARNING",
                text="No active engineering specification available",
                category="Engineering integration",
                source_reference=(
                    "ConfiguratorV2ServiceIntegration._update_active_base_cabinet_dimension"
                ),
            )
            return self.workspace.preview_read_model

        next_specification = copy.copy(current_specification)
        setattr(next_specification, field_name, value)

        result = service.execute(specification=next_specification)
        if not result:
            error_text = "; ".join(tuple(getattr(result, "errors", ()) or ())) or (
                "Engineering service failed"
            )
            self.push_message(
                severity="WARNING",
                text=error_text,
                category="Engineering integration",
                source_reference=(
                    "ConfiguratorV2ServiceIntegration._update_active_base_cabinet_dimension"
                ),
            )
            return self.workspace.preview_read_model

        payload = getattr(result, "data", None) or {}
        cabinet = payload.get("cabinet") if isinstance(payload, dict) else None
        specification = payload.get("specification") if isinstance(payload, dict) else None
        metadata = payload.get("metadata") if isinstance(payload, dict) else {}
        scene_graph = getattr(cabinet, "scene_graph", None) or getattr(cabinet, "graph", None)

        self.workspace.active_engineering_state = ActiveEngineeringState(
            family=getattr(active_state, "family", "") or "Base Cabinet",
            specification=specification,
            cabinet=cabinet,
            scene_graph=scene_graph,
            metadata=dict(metadata) if isinstance(metadata, dict) else {},
            engineering_dirty=False,
            manufacturing_stale=True,
            cost_stale=True,
            commercial_stale=True,
        )
        self.workspace.current_selection = ConfiguratorSelection(
            selection_type="CABINET",
            selection_id="base-cabinet",
            display_name="Base Cabinet",
            source_region="EngineeringApplicationService.execute",
            metadata={},
        )

        preview_source = {
            "scene_graph": scene_graph,
            "preview_title": getattr(self.workspace, "current_product", None) or "Base Cabinet",
            "current_family": getattr(self.workspace, "current_product_family", None) or "Base Cabinet",
            "preview_state": "Ready" if scene_graph is not None else "Unavailable",
            "viewport_message": "Base cabinet engineering model ready"
            if scene_graph is not None
            else "Engineering model did not produce a scene graph",
            "available_representations": ("Customer View", "Design View")
            if scene_graph is not None
            else (),
            "warnings": tuple(getattr(result, "diagnostics", ()) or ()),
            "source_reference": "EngineeringApplicationService.execute",
        }
        if specification is not None:
            preview_source["selection"] = {
                "selection_type": "CABINET",
                "selection_id": "base-cabinet",
                "display_name": "Base Cabinet",
                "metadata": {
                    "width_mm": getattr(specification, "width_mm", ""),
                    "height_mm": getattr(specification, "height_mm", ""),
                    "depth_mm": getattr(specification, "depth_mm", ""),
                    **(metadata if isinstance(metadata, dict) else {}),
                },
        }

        preview = self.refresh_preview(preview_source)
        self.refresh_inspector()

        dimension_label = field_name.replace("_mm", "").replace("_", " ").title()
        self.push_message(
            severity="INFO",
            text=f"Base cabinet {dimension_label} updated",
            category="Engineering integration",
            source_reference=(
                f"ConfiguratorV2ServiceIntegration._update_active_base_cabinet_dimension"
            ),
        )
        return preview

    def update_active_base_cabinet_width(self, width_mm: float):
        """Regenerate the active base cabinet using an updated width only.

        Delegates to ``_update_active_base_cabinet_dimension``.
        """
        return self._update_active_base_cabinet_dimension("width_mm", width_mm)

    def update_active_base_cabinet_height(self, height_mm: float):
        """Regenerate the active base cabinet using an updated height only.

        Delegates to ``_update_active_base_cabinet_dimension``.
        """
        return self._update_active_base_cabinet_dimension("height_mm", height_mm)

    def update_active_base_cabinet_depth(self, depth_mm: float):
        """Regenerate the active base cabinet using an updated depth only.

        Delegates to ``_update_active_base_cabinet_dimension``.
        """
        return self._update_active_base_cabinet_dimension("depth_mm", depth_mm)

    def update_active_base_cabinet_shelf_count(self, shelf_count: int):
        """Regenerate the active base cabinet using an updated shelf count only.

        *shelf_count* must be a non-negative integer.  Delegates to
        ``_update_active_base_cabinet_dimension`` which validates
        integer fields.
        """
        return self._update_active_base_cabinet_dimension("shelf_count", shelf_count)

    def update_active_base_cabinet_door_count(self, door_count: int):
        """Regenerate the active base cabinet using an updated door count only.

        *door_count* must be a non-negative integer.  Delegates to
        ``_update_active_base_cabinet_dimension`` which validates
        integer fields.
        """
        return self._update_active_base_cabinet_dimension("door_count", door_count)

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

    def enrich_manufacturing_review_with_rendering(
        self,
        commands: Any = None,
    ):
        """Add rendering metadata section to the existing Manufacturing panel.

        Accepts an iterable of viewport command dicts. Calls
        ``build_manufacturing_render_review_section`` to extract a
        ``\"Rendering Details\"`` section, then appends it to the
        existing Manufacturing review panel.

        When *commands* is None or empty, the existing Manufacturing
        panel is returned unchanged.  When no Manufacturing panel
        exists yet, a best-effort single-panel tuple is returned.

        This is a pure consumption of existing renderer output — no
        values are recomputed, no manufacturing logic is duplicated.
        """
        if commands is None:
            return tuple(self.workspace.review_panel_read_models or ())

        render_section = build_manufacturing_render_review_section(commands)
        if not render_section.rows:
            return tuple(self.workspace.review_panel_read_models or ())

        existing = tuple(self.workspace.review_panel_read_models or ())
        names = self.workspace.review_panel_names

        def _merge(panel):
            if panel.panel_name != "Manufacturing":
                return panel
            sections = list(panel.sections)
            sections.append(render_section)
            return ReviewPanelReadModel(
                panel_name=panel.panel_name,
                sections=tuple(sections),
                stale=panel.stale,
                available=panel.available,
            )

        merged = tuple(
            _merge(panel) if panel.panel_name == "Manufacturing"
            else panel
            for panel in existing
        )
        if not merged and "Manufacturing" in names:
            merged = (ReviewPanelReadModel(
                panel_name="Manufacturing",
                sections=(render_section,),
            ),)

        self.workspace.set_review_panel_read_models(merged)
        return merged

    def refresh_cost_review(self, source: Any = None):
        if source is None:
            return self._refresh_review_panels(
                source=source,
                message_text="Cost review integration not available yet",
                source_reference="ConfiguratorV2ServiceIntegration.refresh_cost_review",
            )
        panel = build_cost_review_projection(source)
        existing = tuple(self.workspace.review_panel_read_models or ())
        names = self.workspace.review_panel_names
        merged = tuple(
            panel if name == "Cost"
            else existing[i] if i < len(existing)
            else ReviewPanelReadModel(panel_name=name)
            for i, name in enumerate(names)
        )
        self.workspace.set_review_panel_read_models(merged)
        return merged

    def refresh_commercial_review(self, source: Any = None):
        if source is None:
            return self._refresh_review_panels(
                source=source,
                message_text="Commercial review integration not available yet",
                source_reference="ConfiguratorV2ServiceIntegration.refresh_commercial_review",
            )
        panel = build_commercial_review_projection(source)
        existing = tuple(self.workspace.review_panel_read_models or ())
        names = self.workspace.review_panel_names
        merged = tuple(
            panel if name == "Commercial"
            else existing[i] if i < len(existing)
            else ReviewPanelReadModel(panel_name=name)
            for i, name in enumerate(names)
        )
        self.workspace.set_review_panel_read_models(merged)
        return merged

    def refresh_release_review(self, source: Any = None):
        if source is None:
            return self._refresh_review_panels(
                source=source,
                message_text="Release integration not available yet",
                source_reference="ConfiguratorV2ServiceIntegration.refresh_release_review",
            )
        panel = build_release_review_projection(source)
        existing = tuple(self.workspace.review_panel_read_models or ())
        names = self.workspace.review_panel_names
        merged = tuple(
            panel if name == "Release"
            else existing[i] if i < len(existing)
            else ReviewPanelReadModel(panel_name=name)
            for i, name in enumerate(names)
        )
        self.workspace.set_review_panel_read_models(merged)
        return merged

    def refresh_factory_operations(self):
        """Run the full FOI pipeline and store results in workspace.

        Reads the existing 5 review panels from workspace, runs:
        FOI-1 (Readiness) → FOI-2 (Blocking Analysis) → FOI-3 (Recommendations)
        → FOI-4 (Production Decision)

        Then builds a CV2 presentation read model and stores it on workspace.

        Side-effect free on the review panels — the original panels are unchanged.
        """
        review_panels = tuple(self.workspace.review_panel_read_models or ())

        # FOI-1: Readiness
        readiness = build_factory_readiness_read_model(review_panels)

        # FOI-2: Blocking Analysis
        blocking = build_factory_blocking_analysis_read_model(readiness)

        # FOI-3: Recommendations
        recommendations = build_factory_action_recommendation_read_model(blocking)

        # FOI-4: Production Decision
        decision = build_production_decision_read_model(readiness, blocking, recommendations)

        # Store FOI intermediates on workspace for refresh_dashboard to reuse
        self.workspace.set_foi_read_models(
            readiness=readiness,
            blocking=blocking,
            recommendations=recommendations,
            decision=decision,
        )

        # Present as CV2 review panel
        panel = build_foi_presentation_read_model(
            readiness=readiness,
            blocking=blocking,
            recommendations=recommendations,
            decision=decision,
        )
        self.workspace.set_foi_presentation_read_model(panel)
        return panel

    def refresh_dashboard(self):
        """Build a FactoryDashboardReadModel from FOI outputs already stored on workspace.

        Reuses FOI read models produced by the most recent call to
        refresh_factory_operations() — never duplicates the FOI pipeline.

        Returns FactoryDashboardReadModel (or empty read model when no FOI
        data is available).
        """
        readiness = getattr(self.workspace, "_foi_readiness", None)
        blocking = getattr(self.workspace, "_foi_blocking", None)
        recommendations = getattr(self.workspace, "_foi_recommendations", None)
        decision = getattr(self.workspace, "_foi_decision", None)
        nesting_section = self._resolve_nesting_savings_dashboard_section()

        if not any(
            x is not None
            for x in (readiness, blocking, recommendations, decision, nesting_section)
        ):
            empty = self.workspace.factory_dashboard_read_model.__class__() if getattr(
                self.workspace, "factory_dashboard_read_model", None
            ) is not None else build_factory_dashboard_read_model()
            self.workspace.set_factory_dashboard_read_model(empty)
            return empty

        dashboard = build_factory_dashboard_read_model(
            readiness=readiness,
            blocking=blocking,
            recommendations=recommendations,
            decision=decision,
        )
        dashboard = self._append_dashboard_section(dashboard, nesting_section)
        self.workspace.set_factory_dashboard_read_model(dashboard)
        return dashboard

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

    def generate_manufacturing(self, source: Any = None) -> str:
        """Generate manufacturing from an Engineering scene graph.

        Calls ``ManufacturingRuntimePipelineBuilder`` to produce a
        manufacturing package, then refreshes the Manufacturing review
        panel with operation data.

        Returns a status string: "ok", "no_source", or "failed".
        """
        if source is None:
            self.push_message(
                severity="INFO",
                text="Manufacturing generation requires an Engineering scene graph",
                category="Manufacturing integration",
                source_reference="ConfiguratorV2ServiceIntegration.generate_manufacturing",
            )
            return "no_source"

        try:
            runtime_builder = self._resolve_builder_class(
                "manufacturing_runtime_pipeline_builder",
                package_name="manufacturing",
                module_name="manufacturing_runtime_pipeline_builder",
                class_name="ManufacturingRuntimePipelineBuilder",
            )
            package_builder = self._resolve_builder_class(
                "manufacturing_production_package_builder",
                package_name="manufacturing",
                module_name="manufacturing_production_package_builder",
                class_name="ManufacturingProductionPackageBuilder",
            )

            runtime_result = runtime_builder().build(source)
            production_package = package_builder().build(
                runtime_result.manufacturing_package
            )
            self.workspace.set_manufacturing_result(production_package)

            # Refresh Manufacturing review panel
            self.workspace.set_review_panel_read_models(
                self._merge_review_panel(
                    "Manufacturing",
                    build_manufacturing_review_projection(
                        self._manufacturing_operations(production_package)
                    ),
                )
            )

            self.push_message(
                severity="INFO",
                text="Manufacturing generated successfully",
                category="Manufacturing integration",
                source_reference="ConfiguratorV2ServiceIntegration.generate_manufacturing",
            )
            return "ok"
        except Exception as exc:
            self.push_message(
                severity="WARNING",
                text=f"Manufacturing generation failed: {exc}",
                category="Manufacturing integration",
                source_reference="ConfiguratorV2ServiceIntegration.generate_manufacturing",
            )
            return "failed"

    def review_cost(self) -> str:
        """Review cost from stored production package.

        Calls ``ManufacturingCostPipelineBuilder`` with the stored
        production package, then refreshes the Cost review panel.

        Returns a status string: "ok", "no_manufacturing", or "failed".
        """
        production_package = getattr(
            self.workspace, "_manufacturing_production_package", None
        )
        if production_package is None:
            self.push_message(
                severity="INFO",
                text="Cost review requires manufacturing to be generated first",
                category="Cost integration",
                source_reference="ConfiguratorV2ServiceIntegration.review_cost",
            )
            return "no_manufacturing"

        try:
            cost_builder = self._resolve_builder_class(
                "manufacturing_cost_pipeline_builder",
                package_name="cost_intelligence",
                module_name="manufacturing_cost_pipeline_builder",
                class_name="ManufacturingCostPipelineBuilder",
            )

            cost_summary = cost_builder().build(production_package)
            self.workspace.set_cost_result(cost_summary)

            cost_items = self._cost_items_from_summary(cost_summary)
            self.workspace.set_review_panel_read_models(
                self._merge_review_panel(
                    "Cost",
                    build_cost_review_projection({"cost_items": cost_items}),
                )
            )

            self.push_message(
                severity="INFO",
                text="Cost review completed",
                category="Cost integration",
                source_reference="ConfiguratorV2ServiceIntegration.review_cost",
            )
            return "ok"
        except Exception as exc:
            self.push_message(
                severity="WARNING",
                text=f"Cost review failed: {exc}",
                category="Cost integration",
                source_reference="ConfiguratorV2ServiceIntegration.review_cost",
            )
            return "failed"

    def review_commercial(self, *, markup_rate: float = 0.0, currency: str = "MAD") -> str:
        """Review commercial from stored cost summary.

        Calls ``ManufacturingCommercialPipelineBuilder`` with the stored
        cost summary, then refreshes the Commercial review panel.

        Returns a status string: "ok", "no_cost", or "failed".
        """
        cost_summary = getattr(
            self.workspace, "_manufacturing_cost_summary", None
        )
        if cost_summary is None:
            self.push_message(
                severity="INFO",
                text="Commercial review requires cost review first",
                category="Commercial integration",
                source_reference="ConfiguratorV2ServiceIntegration.review_commercial",
            )
            return "no_cost"

        try:
            commercial_builder = self._resolve_builder_class(
                "manufacturing_commercial_pipeline_builder",
                package_name="cost_intelligence",
                module_name="manufacturing_commercial_pipeline_builder",
                class_name="ManufacturingCommercialPipelineBuilder",
            )
            production_package = getattr(
                self.workspace, "_manufacturing_production_package", None
            )
            commercial_result = commercial_builder().build(
                production_package,
                markup_rate,
                currency,
                manufacturing_cost_summary=cost_summary,
            )
            self.workspace.set_commercial_result(commercial_result)

            commercial_items = self._commercial_items_from_result(commercial_result)
            self.workspace.set_review_panel_read_models(
                self._merge_review_panel(
                    "Commercial",
                    build_commercial_review_projection(
                        {"commercial_items": commercial_items}
                    ),
                )
            )

            self.push_message(
                severity="INFO",
                text="Commercial review completed",
                category="Commercial integration",
                source_reference="ConfiguratorV2ServiceIntegration.review_commercial",
            )
            return "ok"
        except Exception as exc:
            self.push_message(
                severity="WARNING",
                text=f"Commercial review failed: {exc}",
                category="Commercial integration",
                source_reference="ConfiguratorV2ServiceIntegration.review_commercial",
            )
            return "failed"

    # ── internal helpers ───────────────────────────────────────────

    def _merge_review_panel(
        self, panel_name: str, panel: Any
    ) -> tuple[ReviewPanelReadModel, ...]:
        from .read_models import ReviewPanelReadModel as _RPM

        existing = tuple(self.workspace.review_panel_read_models or ())
        names = self.workspace.review_panel_names
        return tuple(
            panel if name == panel_name
            else existing[i] if i < len(existing)
            else _RPM(panel_name=name)
            for i, name in enumerate(names)
        )

    def _resolve_nesting_savings_dashboard_section(self):
        section = getattr(self.workspace, "_nesting_savings_dashboard_section", None)
        if section is not None:
            return section
        savings_report = getattr(self.workspace, "_nesting_savings_report", None)
        if savings_report is None:
            return None
        return build_nesting_savings_dashboard_section(savings_report)

    @staticmethod
    def _append_dashboard_section(dashboard: Any, section: Any):
        if dashboard is None or section is None:
            return dashboard
        dashboard_type = dashboard.__class__
        sections = list(tuple(getattr(dashboard, "sections", ()) or ()))
        sections.append(section)
        return dashboard_type(
            sections=tuple(sections),
            factory_status=getattr(dashboard, "factory_status", "") or "",
            decision_status=getattr(dashboard, "decision_status", "") or "",
            critical_blocker_count=getattr(dashboard, "critical_blocker_count", 0) or 0,
            recommendation_count=getattr(dashboard, "recommendation_count", 0) or 0,
            summary_message=getattr(dashboard, "summary_message", "") or "",
            available=True,
        )

    @staticmethod
    def _manufacturing_operations(production_package: Any) -> list[dict[str, str]]:
        operations = []
        reports = [
            getattr(production_package, attr, None)
            for attr in (
                "cutlist_report", "edge_report", "machining_report",
                "cnc_report", "assembly_report", "hardware_report",
            )
        ]
        for report in reports:
            if report is None:
                continue
            items = getattr(report, "items", None) or getattr(report, "operations", None) or ()
            report_name = getattr(report, "__class__", type(report)).__name__
            count = len(items) if hasattr(items, "__len__") else 0
            operations.append({
                "operation_label": report_name.replace("Report", ""),
                "operation_status": "PASS" if count > 0 else "INFO",
                "operation_message": f"{count} item(s)",
            })
        return operations

    @staticmethod
    def _cost_items_from_summary(cost_summary: Any) -> list[dict[str, str]]:
        cost = getattr(cost_summary, "cost_report", None) or cost_summary
        items = []
        _fields = [
            ("material_cost", "Material", "Material"),
            ("sheet_cost", "Material", "Sheet Cost"),
            ("waste_cost", "Waste", "Waste"),
            ("edge_banding_cost", "Material", "Edge Banding"),
            ("drilling_cost", "Material", "Machining"),
            ("hardware_cost", "Hardware", "Hardware"),
            ("complexity_cost", "Material", "Complexity"),
            ("panel_handling_cost", "Material", "Panel Handling"),
            ("cnc_labor_cost", "Labor", "CNC Labor"),
            ("drilling_labor_cost", "Labor", "Drilling Labor"),
            ("edge_banding_labor_cost", "Labor", "Edge Banding Labor"),
            ("assembly_labor_cost", "Labor", "Assembly Labor"),
            ("total_labor_cost", "Labor", "Total Labor"),
            ("overhead_cost", "Other", "Overhead"),
            ("recovered_value", "Other", "Recovered Value"),
            ("net_material_cost", "Material", "Net Material"),
        ]
        for field, category, label in _fields:
            raw = float(getattr(cost, field, 0.0) or 0.0)
            if raw:
                items.append({
                    "item_label": label,
                    "item_category": category,
                    "item_amount": f"{raw:.2f}",
                })
        total = float(getattr(cost, "total_manufacturing_cost", 0.0) or 0.0)
        items.append({
            "item_label": "Total Manufacturing Cost",
            "item_category": "Totals",
            "item_amount": f"{total:.2f}",
        })
        return items

    @staticmethod
    def _commercial_items_from_result(commercial_result: Any) -> list[dict[str, str]]:
        items = []
        summary = getattr(commercial_result, "manufacturing_cost_summary", None)
        if summary is not None:
            total = float(
                getattr(summary, "total_manufacturing_cost", 0.0) or 0.0
            )
            items.append({
                "item_label": "Production Cost",
                "item_category": "Pricing",
                "item_value": f"{total:.2f}",
            })
        quotation = getattr(commercial_result, "quotation_report", None)
        if quotation is not None:
            for label, field in (
                ("Production Cost", "production_cost"),
                ("Markup Rate", "markup_rate"),
                ("Markup Amount", "markup_amount"),
                ("Selling Price", "selling_price"),
            ):
                raw = float(getattr(quotation, field, 0.0) or 0.0)
                items.append({
                    "item_label": label,
                    "item_category": "Pricing" if label in ("Production Cost", "Markup Rate") else "Summary",
                    "item_value": f"{raw:.2f}" if field != "markup_rate" else f"{raw:.0%}",
                })
            items.append({
                "item_label": "Currency",
                "item_category": "Summary",
                "item_value": str(getattr(quotation, "currency", "MAD")),
            })
        profitability = getattr(commercial_result, "profitability_report", None)
        if profitability is not None:
            for label, field in (
                ("Gross Profit", "gross_profit"),
                ("Gross Margin Rate", "gross_margin_rate"),
                ("Status", "profitability_status"),
            ):
                raw = getattr(profitability, field, None)
                if raw is not None:
                    items.append({
                        "item_label": label,
                        "item_category": "Summary",
                        "item_value": f"{raw:.2%}" if field == "gross_margin_rate" else str(raw),
                    })
        return items


@dataclass(frozen=True)
class EngineeringProjectionResult:
    """Read-only result of projecting Engineering source through the adapter pipeline.

    All fields are CV2-native frozen dataclasses — no Engineering types,
    no domain types, and no backend geometry objects.

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
