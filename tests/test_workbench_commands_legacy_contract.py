import importlib
import sys
import types
import unittest
from types import SimpleNamespace
from unittest.mock import patch


class FakeWardrobeBuilder:
    instances_created = 0
    build_calls = 0
    divider_calls = 0
    shelves_calls = 0
    doors_calls = 0

    def __init__(self, *args, **kwargs):
        type(self).instances_created += 1

    def add_divider(self, *args, **kwargs):
        type(self).divider_calls += 1
        return ("LEFT", "RIGHT")

    def add_shelves(self, *args, **kwargs):
        type(self).shelves_calls += 1

    def add_doors(self, *args, **kwargs):
        type(self).doors_calls += 1

    def build(self):
        type(self).build_calls += 1
        return SimpleNamespace(
            graph=SimpleNamespace(physical_nodes=[]),
            joinery=SimpleNamespace(edges=[]),
        )


class TestWorkbenchCommandsLegacyContract(unittest.TestCase):
    @staticmethod
    def _fake_runtime_modules():
        fake_freecad_gui = types.ModuleType("FreeCADGui")
        fake_freecad_gui.listCommands = lambda: []
        fake_freecad_gui.addCommand = lambda *args, **kwargs: None
        fake_freecad_gui.addWorkbench = lambda *args, **kwargs: None
        fake_freecad = types.ModuleType("FreeCAD")
        fake_part = types.ModuleType("Part")
        fake_renderer = types.ModuleType("gui.renderer")
        fake_renderer.GeometryRenderer = type(
            "GeometryRenderer",
            (),
            {"render": staticmethod(lambda *args, **kwargs: None)},
        )
        return {
            "FreeCADGui": fake_freecad_gui,
            "FreeCAD": fake_freecad,
            "Part": fake_part,
            "gui.renderer": fake_renderer,
        }

    @classmethod
    def _import_commands_module(cls):
        runtime_modules = cls._fake_runtime_modules()
        with patch.dict(sys.modules, runtime_modules):
            commands_module = importlib.import_module("commands.workbench_commands")
        return commands_module, runtime_modules

    def test_create_wardrobe_command_still_uses_legacy_wardrobe_builder(self):
        commands_module, runtime_modules = self._import_commands_module()
        import domain.builders as builders_module
        import domain.manufacturing_compiler as manufacturing_compiler_module
        import domain.rules_engine as rules_engine_module

        FakeWardrobeBuilder.instances_created = 0
        FakeWardrobeBuilder.build_calls = 0
        FakeWardrobeBuilder.divider_calls = 0
        FakeWardrobeBuilder.shelves_calls = 0
        FakeWardrobeBuilder.doors_calls = 0

        with patch.object(
            builders_module,
            "WardrobeBuilder",
            new=FakeWardrobeBuilder,
        ), patch.object(
            rules_engine_module,
            "HardwarePlacementEngine",
        ) as hardware_engine_cls, patch.object(
            manufacturing_compiler_module,
            "ManufacturingCompiler",
        ) as compiler_cls, patch.dict(sys.modules, runtime_modules):
            hardware_engine_cls.return_value.process.return_value = None
            compiler_cls.return_value.compile.return_value = None
            commands_module.CreateWardrobeCommand().Activated()

        self.assertEqual(FakeWardrobeBuilder.instances_created, 1)
        self.assertEqual(FakeWardrobeBuilder.divider_calls, 1)
        self.assertEqual(FakeWardrobeBuilder.shelves_calls, 0)
        self.assertEqual(FakeWardrobeBuilder.doors_calls, 0)
        self.assertEqual(FakeWardrobeBuilder.build_calls, 1)

    def test_manufacturing_geometry_command_still_uses_legacy_wardrobe_builder(self):
        commands_module, runtime_modules = self._import_commands_module()
        import cost_intelligence.manufacturing_cost_pipeline_builder as cost_builder_module
        import domain.builders as builders_module
        import domain.manufacturing_compiler as manufacturing_compiler_module
        import domain.rules_engine as rules_engine_module
        import manufacturing.engineering_demonstration_report as engineering_report_module
        import manufacturing.manufacturing_runtime_pipeline_builder as runtime_builder_module
        import services.manufacturing_validation_service as validation_service_module

        FakeWardrobeBuilder.instances_created = 0
        FakeWardrobeBuilder.build_calls = 0
        FakeWardrobeBuilder.divider_calls = 0
        FakeWardrobeBuilder.shelves_calls = 0
        FakeWardrobeBuilder.doors_calls = 0

        with patch.object(
            builders_module,
            "WardrobeBuilder",
            new=FakeWardrobeBuilder,
        ), patch.object(
            rules_engine_module,
            "HardwarePlacementEngine",
        ) as hardware_engine_cls, patch.object(
            manufacturing_compiler_module,
            "ManufacturingCompiler",
        ) as compiler_cls, patch.object(
            validation_service_module,
            "ManufacturingValidationService",
        ) as validation_service_cls, patch.object(
            runtime_builder_module,
            "ManufacturingRuntimePipelineBuilder",
        ) as runtime_builder_cls, patch.object(
            cost_builder_module,
            "ManufacturingCostPipelineBuilder",
        ) as cost_builder_cls, patch.object(
            engineering_report_module,
            "build_engineering_demonstration_report",
        ) as report_builder, patch.dict(sys.modules, runtime_modules):
            hardware_engine_cls.return_value.process.return_value = None
            compiler_cls.return_value.compile.return_value = None
            validation_service_cls.validate.return_value = SimpleNamespace()
            runtime_builder_cls.return_value.build.return_value = SimpleNamespace(
                manufacturing_production_package=SimpleNamespace()
            )
            cost_builder_cls.return_value.build.return_value = SimpleNamespace()
            report_builder.return_value = SimpleNamespace()
            commands_module.CreateEngineeringDemonstrationCommand().Activated()

        self.assertEqual(FakeWardrobeBuilder.instances_created, 1)
        self.assertEqual(FakeWardrobeBuilder.divider_calls, 1)
        self.assertEqual(FakeWardrobeBuilder.shelves_calls, 2)
        self.assertEqual(FakeWardrobeBuilder.doors_calls, 1)
        self.assertEqual(FakeWardrobeBuilder.build_calls, 1)


if __name__ == "__main__":
    unittest.main()
