import ast
import inspect
import unittest
from importlib import import_module
from types import ModuleType
from unittest.mock import patch


def _imported_modules(module):
    source = inspect.getsource(module)
    tree = ast.parse(source)
    imported_modules = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.append(node.module)
    return {module.lower() for module in imported_modules}


class TestWallGeometryExecutionBoundaryContract(unittest.TestCase):
    @staticmethod
    def _import_cabinet_builder_module():
        fake_freecad = ModuleType("FreeCAD")
        fake_part = ModuleType("Part")
        fake_freecad_gui = ModuleType("FreeCADGui")

        with patch.dict(
            "sys.modules",
            {
                "FreeCAD": fake_freecad,
                "Part": fake_part,
                "FreeCADGui": fake_freecad_gui,
            },
        ):
            return import_module("engine.cabinet_builder")

    @staticmethod
    def _import_wall_panel_geometry_module():
        try:
            return import_module("engine.wall_panel_geometry")
        except ModuleNotFoundError:
            raise AssertionError(
                "Missing contract target: expected module "
                "'engine.wall_panel_geometry' exposing "
                "'build_wall_panel_geometry(placements)'."
            )

    def test_cabinet_builder_remains_geometry_orchestration_boundary(self):
        cabinet_builder_module = self._import_cabinet_builder_module()
        signature = inspect.signature(cabinet_builder_module.CabinetBuilder.build)

        self.assertEqual(list(signature.parameters), ["self", "cabinet"])

        source = inspect.getsource(cabinet_builder_module)
        for token in (
            "ManufacturingRuntimePipelineBuilder",
            "ManufacturingPackageBuilder",
            "ManufacturingProductionPackageBuilder",
            "CostPackageBuilder",
            "CommercialPackageBuilder",
            "ProductFamily",
            "ProductConfiguration",
        ):
            self.assertNotIn(token, source)

    def test_wall_geometry_entrypoint_consumes_placements_only(self):
        module = self._import_wall_panel_geometry_module()
        build_fn = getattr(module, "build_wall_panel_geometry", None)
        if not callable(build_fn):
            self.fail(
                "Missing contract target: expected callable "
                "'engine.wall_panel_geometry.build_wall_panel_geometry'."
            )

        signature = inspect.signature(build_fn)
        self.assertEqual(list(signature.parameters), ["placements"])

    def test_wall_geometry_has_no_manufacturing_cost_or_commercial_dependency(self):
        module = self._import_wall_panel_geometry_module()
        imports = _imported_modules(module)

        for forbidden in ("manufacturing", "cost", "commercial"):
            self.assertFalse(
                any(
                    imported == forbidden or imported.startswith(f"{forbidden}.")
                    for imported in imports
                ),
                msg=f"unexpected dependency found in {sorted(imports)!r}",
            )

    def test_wall_geometry_does_not_classify_product_families(self):
        module = self._import_wall_panel_geometry_module()
        source = inspect.getsource(module)
        for token in ("ProductFamily", "ProductConfiguration", "family_classifier"):
            self.assertNotIn(token, source)

    def test_wall_geometry_has_no_cabinet_registration_or_rendering_dependency(self):
        module = self._import_wall_panel_geometry_module()
        imports = _imported_modules(module)

        for forbidden in (
            "scene_graph",
            "services.project_service",
            "assembly",
            "builders.hardware_builder",
            "freecad",
            "freecadgui",
            "part",
        ):
            self.assertFalse(
                any(
                    imported == forbidden or imported.startswith(f"{forbidden}.")
                    for imported in imports
                ),
                msg=f"unexpected dependency found in {sorted(imports)!r}",
            )


if __name__ == "__main__":
    unittest.main()
