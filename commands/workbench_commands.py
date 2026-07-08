import FreeCADGui


class OpenConfiguratorCommand:

    def GetResources(self):
        return {
            'Pixmap': '',
            'MenuText': 'Configurator',
            'ToolTip': 'Open Pro Dressing Configurator'
        }

    def Activated(self):
        from ui.main_window import UIManager

        global dressing_app

        try:
            dressing_app.close()
        except Exception:
            pass

        dressing_app = UIManager()
        dressing_app.show()

    def IsActive(self):
        return True


def _open_configurator_v2():
    """Private helper — instantiate and show a fully wired Configurator V2 workspace.

    Lazy imports ensure FreeCAD-bound modules are loaded only when this
    helper is called (inside ``Activated()``), preserving test isolation
    for ``ui.configurator_v2``.

    Returns the workspace widget for testing.
    """
    from ui.configurator_v2 import (
        create_configurator_v2_workspace,
        ConfiguratorV2ServiceBindings,
    )
    from ui.configurator_v2.service_integration import attach_service_integration
    from application.engineering_application_service import EngineeringApplicationService

    service = EngineeringApplicationService()
    bindings = ConfiguratorV2ServiceBindings(
        engineering_application_service=service,
    )
    workspace = create_configurator_v2_workspace(service_bindings=bindings)
    integration = attach_service_integration(workspace, bindings)
    workspace.set_project_context(current_product_family="Base Cabinet")
    integration.create_base_cabinet()
    workspace.show()
    return workspace


class OpenConfiguratorV2Command:

    def GetResources(self):
        return {
            'Pixmap': '',
            'MenuText': 'Configurator V2',
            'ToolTip': 'Open SmartFurniture Configurator V2 with live editing',
        }

    def Activated(self):
        _open_configurator_v2()

    def IsActive(self):
        return True


class CreateWardrobeCommand:

    def GetResources(self):
        return {
            'Pixmap': '',
            'MenuText': 'Create Wardrobe',
            'ToolTip': 'Create demo wardrobe and render it'
        }

    def Activated(self):

        from domain.builders import WardrobeBuilder

        from domain.rules_engine import (
            HardwarePlacementEngine,
            RuleContext
        )

        from domain.manufacturing_compiler import (
            ManufacturingCompiler
        )

        from gui.renderer import GeometryRenderer

        cab = WardrobeBuilder(
            uid="DEMO",
            width=1200,
            height=2400,
            depth=600
        )

        cab.add_divider(600)

        project = cab.build()

        context = RuleContext()

        HardwarePlacementEngine(
            context
        ).process(project)

        ManufacturingCompiler().compile(
            project,
            context
        )

        GeometryRenderer.render(project)

    def IsActive(self):
        return True


class CreateEngineeringDemonstrationCommand:

    def GetResources(self):
        return {
            "Pixmap": "",
            "MenuText": "Manufacturing Geometry",
            "ToolTip": "Build a visible manufacturing geometry cabinet",
        }

    def Activated(self):
        from cost_intelligence.manufacturing_cost_pipeline_builder import (
            ManufacturingCostPipelineBuilder,
        )
        from domain.builders import WardrobeBuilder
        from domain.rules_engine import HardwarePlacementEngine, RuleContext
        from manufacturing.engineering_demonstration_report import (
            build_engineering_demonstration_report,
        )
        from manufacturing.manufacturing_runtime_pipeline_builder import (
            ManufacturingRuntimePipelineBuilder,
        )
        from services.manufacturing_validation_service import (
            ManufacturingValidationService,
        )
        from domain.manufacturing_compiler import ManufacturingCompiler
        from gui.renderer import GeometryRenderer

        cabinet = WardrobeBuilder(
            uid="VISIBLE_ENGINEERING_DEMO",
            width=1200,
            height=2400,
            depth=600,
        )

        left_section, right_section = cabinet.add_divider(600)
        cabinet.add_shelves(2, left_section)
        cabinet.add_shelves(2, right_section)
        cabinet.add_doors(2)

        project = cabinet.build()

        context = RuleContext()
        HardwarePlacementEngine(context).process(project)
        ManufacturingCompiler().compile(project, context)

        validation_state = ManufacturingValidationService.validate(project.graph)
        runtime_result = ManufacturingRuntimePipelineBuilder().build(project.graph)
        cost_summary = ManufacturingCostPipelineBuilder().build(
            runtime_result.manufacturing_production_package
        )
        engineering_report = build_engineering_demonstration_report(
            project,
            validation_state=validation_state,
            cost_summary=cost_summary,
        )

        GeometryRenderer.render(
            project,
            engineering_report=engineering_report,
        )

    def IsActive(self):
        return True
