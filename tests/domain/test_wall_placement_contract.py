import ast
import importlib
import inspect
import unittest
from typing import get_type_hints

from domain.wall_cabinet_construction_mapper import (
    build_wall_cabinet_construction_model,
)
from domain.furniture_construction_model import CabinetConstructionModel
from domain.wall_cabinet_engineering_model import WallCabinetEngineeringModel
from domain.wall_cabinet_specification import WallCabinetSpecification


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


def _read(subject, key):
    if isinstance(subject, dict):
        return subject[key]
    return getattr(subject, key)


class TestWallPlacementContract(unittest.TestCase):
    def setUp(self):
        self.specification = WallCabinetSpecification(
            width_mm=720.0,
            height_mm=900.0,
            depth_mm=380.0,
            door_count=2,
            shelf_count=2,
            has_back_panel=True,
            hinge_family="STANDARD_110",
            suspension_hardware_family="CONCEALED_BRACKET",
            wall_type="MASONRY",
            max_load_kg=35.0,
            required_clearance_mm=45.0,
        )
        self.engineering_model = WallCabinetEngineeringModel(
            specification=self.specification,
        )
        self.construction_model = build_wall_cabinet_construction_model(
            self.specification
        )

    def _build_wall_placements(self):
        try:
            module = importlib.import_module("domain.wall_placement_builder")
        except ModuleNotFoundError as exc:
            self.fail(
                "Missing contract target: expected module "
                "'domain.wall_placement_builder' exposing "
                "'build_wall_placements(engineering_model, construction_model)'. "
                "This contract-first sprint defines the required output, but the "
                "transient builder does not exist yet."
            )

        build_fn = getattr(module, "build_wall_placements", None)
        if not callable(build_fn):
            self.fail(
                "Missing contract target: expected callable "
                "'domain.wall_placement_builder.build_wall_placements'."
            )

        return build_fn(
            engineering_model=self.engineering_model,
            construction_model=self.construction_model,
        )

    def _assert_panel_contract(
        self,
        panel,
        *,
        role,
        expected_dimension_pair,
        require_zero_origin=False,
    ):
        spec = self.construction_model.specification
        self.assertEqual(_read(panel, "role"), role)
        self.assertTrue(str(_read(panel, "name")).strip())

        width_mm = _read(panel, "width_mm")
        depth_mm = _read(panel, "depth_mm")
        height_mm = _read(panel, "height_mm")
        thickness_mm = _read(panel, "thickness_mm")
        x_mm, y_mm, z_mm = _read(panel, "position_mm")

        self.assertGreater(width_mm, 0.0)
        self.assertGreater(depth_mm, 0.0)
        self.assertGreater(height_mm, 0.0)
        self.assertGreater(thickness_mm, 0.0)
        self.assertLessEqual(width_mm, spec.width_mm)
        self.assertLessEqual(depth_mm, spec.depth_mm)
        self.assertLessEqual(height_mm, spec.height_mm)
        self.assertGreaterEqual(x_mm, 0.0)
        self.assertGreaterEqual(y_mm, 0.0)
        self.assertGreaterEqual(z_mm, 0.0)
        self.assertLessEqual(x_mm, spec.width_mm)
        self.assertLessEqual(y_mm, spec.depth_mm)
        self.assertLessEqual(z_mm, spec.height_mm)

        expected_a, expected_b = expected_dimension_pair
        self.assertIn(expected_a, (width_mm, depth_mm, height_mm))
        self.assertIn(expected_b, (width_mm, depth_mm, height_mm))

        coordinate_meaning = _read(panel, "coordinate_meaning")
        self.assertTrue(str(coordinate_meaning).strip())

        if require_zero_origin:
            self.assertEqual((x_mm, y_mm, z_mm), (0.0, 0.0, 0.0))

    def test_builder_exposes_contract_entrypoint(self):
        self._build_wall_placements()

    def test_builder_accepts_engineering_model_and_construction_model_inputs(self):
        try:
            module = importlib.import_module("domain.wall_placement_builder")
        except ModuleNotFoundError:
            self.fail("Missing contract target: domain.wall_placement_builder")

        build_fn = getattr(module, "build_wall_placements", None)
        if not callable(build_fn):
            self.fail(
                "Missing contract target: expected callable "
                "'domain.wall_placement_builder.build_wall_placements'."
            )

        signature = inspect.signature(build_fn)
        self.assertEqual(
            list(signature.parameters),
            ["engineering_model", "construction_model"],
        )
        hints = get_type_hints(build_fn)
        self.assertIs(hints.get("engineering_model"), WallCabinetEngineeringModel)
        self.assertIs(hints.get("construction_model"), CabinetConstructionModel)

    def test_left_side_panel_placement_contract(self):
        """Input: wall engineering + construction models.

        Expected placement: one side-panel placement category exists.
        Expected coordinate meaning: panel position is cabinet-local.
        Expected orientation: implementation-defined.
        Expected invariants: panel dimensions remain consistent with cabinet thickness, depth, and height.
        """
        placements = self._build_wall_placements()
        spec = self.construction_model.specification
        panel = _read(placements, "left_side_panel")
        self._assert_panel_contract(
            panel,
            role="SIDE_PANEL",
            expected_dimension_pair=(spec.material_thickness_mm, spec.height_mm),
            require_zero_origin=True,
        )

    def test_right_side_panel_placement_contract(self):
        """Input: wall engineering + construction models.

        Expected placement: second side-panel placement category exists.
        Expected coordinate meaning: panel position is cabinet-local.
        Expected orientation: implementation-defined.
        Expected invariants: panel dimensions remain consistent with cabinet thickness, depth, and height.
        """
        placements = self._build_wall_placements()
        spec = self.construction_model.specification
        panel = _read(placements, "right_side_panel")
        self._assert_panel_contract(
            panel,
            role="SIDE_PANEL",
            expected_dimension_pair=(spec.material_thickness_mm, spec.height_mm),
        )
        left_panel = _read(placements, "left_side_panel")
        self.assertNotEqual(_read(panel, "position_mm"), _read(left_panel, "position_mm"))

    def test_top_panel_placement_contract(self):
        """Input: wall engineering + construction models.

        Expected placement: top panel category exists.
        Expected coordinate meaning: panel position is cabinet-local.
        Expected orientation: implementation-defined.
        Expected invariants: one dimension equals cabinet thickness and one equals the inner span.
        """
        placements = self._build_wall_placements()
        spec = self.construction_model.specification
        thickness = spec.material_thickness_mm
        inner_width = spec.width_mm - (2 * thickness)
        panel = _read(placements, "top_panel")
        self._assert_panel_contract(
            panel,
            role="TOP_PANEL",
            expected_dimension_pair=(thickness, inner_width),
        )

    def test_bottom_panel_placement_contract(self):
        """Input: wall engineering + construction models.

        Expected placement: bottom panel category exists.
        Expected coordinate meaning: panel position is cabinet-local.
        Expected orientation: implementation-defined.
        Expected invariants: one dimension equals cabinet thickness and one equals the inner span.
        """
        placements = self._build_wall_placements()
        spec = self.construction_model.specification
        thickness = spec.material_thickness_mm
        inner_width = spec.width_mm - (2 * thickness)
        panel = _read(placements, "bottom_panel")
        self._assert_panel_contract(
            panel,
            role="BOTTOM_PANEL",
            expected_dimension_pair=(thickness, inner_width),
        )

    def test_back_panel_placement_contract(self):
        """Input: wall engineering + construction models.

        Expected placement: back-panel category exists.
        Expected coordinate meaning: panel position is cabinet-local.
        Expected orientation: implementation-defined.
        Expected invariants: placement preserves construction back-panel installation metadata.
        """
        placements = self._build_wall_placements()
        spec = self.construction_model.specification
        thickness = spec.material_thickness_mm
        inner_width = spec.width_mm - (2 * thickness)
        back = _read(placements, "back_panel")

        self.assertEqual(_read(back, "role"), "BACK_PANEL")
        self.assertTrue(str(_read(back, "name")).strip())
        self.assertEqual(_read(back, "width_mm"), inner_width)
        self.assertEqual(_read(back, "depth_mm"), spec.back_panel_thickness_mm)
        self.assertEqual(_read(back, "height_mm"), spec.height_mm - (2 * thickness))
        self.assertEqual(_read(back, "thickness_mm"), spec.back_panel_thickness_mm)
        position_mm = _read(back, "position_mm")
        self.assertEqual(len(position_mm), 3)
        self.assertTrue(str(_read(back, "coordinate_meaning")).strip())
        self.assertEqual(
            _read(back, "installation_mode"),
            self.construction_model.back_panel.installation_mode,
        )
        self.assertEqual(
            _read(back, "placement"),
            self.construction_model.back_panel.placement,
        )
        self.assertEqual(
            _read(back, "groove_depth_mm"),
            self.construction_model.back_panel.groove_depth_mm,
        )
        self.assertEqual(
            _read(back, "groove_width_mm"),
            self.construction_model.back_panel.groove_width_mm,
        )

    def test_cabinet_origin_and_local_coordinate_system_contract(self):
        """Input: wall engineering + construction models.

        Expected placement: cabinet origin exists and anchors local references.
        Expected coordinate meaning: cabinet-local frame.
        Expected orientation: implementation-defined.
        Expected invariants: origin and coordinate system share the same origin.
        """
        placements = self._build_wall_placements()

        self.assertEqual(_read(placements, "cabinet_origin_mm"), (0.0, 0.0, 0.0))

        local_cs = _read(placements, "local_coordinate_system")
        self.assertEqual(_read(local_cs, "origin_mm"), (0.0, 0.0, 0.0))
        self.assertIsNotNone(local_cs)

    def test_wall_reference_plane_and_clearance_contract(self):
        """Input: wall engineering + construction models.

        Expected placement: wall reference plane and clearance reference exist.
        Expected coordinate meaning: both are expressed in cabinet-local terms.
        Expected orientation: implementation-defined.
        Expected invariants: wall plane is dimensionally consistent with cabinet depth and clearance preserves semantic input.
        """
        placements = self._build_wall_placements()
        spec = self.construction_model.specification

        plane = _read(placements, "wall_reference_plane")
        self.assertTrue(str(_read(plane, "reference_face")).strip())
        self.assertGreaterEqual(_read(plane, "offset_mm"), 0.0)
        self.assertLessEqual(_read(plane, "offset_mm"), spec.depth_mm)
        self.assertTrue(str(_read(plane, "coordinate_meaning")).strip())

        clearance = _read(placements, "wall_clearance_reference")
        self.assertEqual(
            _read(clearance, "required_clearance_mm"),
            self.engineering_model.required_clearance_mm,
        )
        self.assertTrue(str(_read(clearance, "reference_face")).strip())
        self.assertTrue(str(_read(clearance, "coordinate_meaning")).strip())

    def test_wall_mount_reference_points_contract(self):
        """Input: wall engineering + construction models.

        Expected placement: one or more wall-mount reference points on the rear reference plane.
        Expected coordinate meaning: each position_mm is in cabinet-local mm.
        Expected orientation: implementation-defined.
        Expected invariants: count is deterministic and preserves wall engineering metadata.
        """
        placements = self._build_wall_placements()
        spec = self.construction_model.specification
        points = tuple(_read(placements, "wall_mount_reference_points"))

        self.assertEqual(len(points), spec.wall_mount_count)
        self.assertGreater(len(points), 0)

        for index, point in enumerate(points):
            x_mm, y_mm, z_mm = _read(point, "position_mm")
            self.assertEqual(_read(point, "mount_index"), index)
            self.assertTrue(str(_read(point, "coordinate_meaning")).strip())
            self.assertEqual(
                _read(point, "hardware_family"),
                self.engineering_model.suspension_hardware_family,
            )
            self.assertEqual(_read(point, "wall_type"), self.engineering_model.wall_type)
            self.assertEqual(_read(point, "max_load_kg"), self.engineering_model.max_load_kg)
            self.assertEqual(
                _read(point, "required_clearance_mm"),
                self.engineering_model.required_clearance_mm,
            )
            self.assertGreaterEqual(x_mm, 0.0)
            self.assertLessEqual(x_mm, spec.width_mm)
            self.assertGreaterEqual(y_mm, 0.0)
            self.assertLessEqual(y_mm, spec.depth_mm)
            self.assertGreaterEqual(z_mm, 0.0)
            self.assertLessEqual(z_mm, spec.height_mm)

    def test_deterministic_placement_ordering_contract(self):
        """Input: identical wall engineering + construction models across repeated calls.

        Expected placement: stable panel ordering and stable mount-point ordering.
        Expected coordinate meaning: identical inputs must yield identical tuples.
        Expected orientation: unchanged across repeated derivation.
        Expected invariants: deterministic ordering is part of the builder contract.
        """
        first = self._build_wall_placements()
        second = self._build_wall_placements()

        ordered_panel_keys = tuple(_read(first, "ordered_panel_keys"))
        self.assertEqual(
            set(ordered_panel_keys),
            {
                "left_side_panel",
                "right_side_panel",
                "top_panel",
                "bottom_panel",
                "back_panel",
            },
        )
        self.assertEqual(tuple(_read(second, "ordered_panel_keys")), ordered_panel_keys)
        self.assertEqual(first, second)

    def test_builder_has_no_geometry_dependency(self):
        try:
            module = importlib.import_module("domain.wall_placement_builder")
        except ModuleNotFoundError:
            self.fail("Missing contract target: domain.wall_placement_builder")

        imports = _imported_modules(module)
        for forbidden in ("engine.geometry_engine", "geometry", "layout", "validation"):
            self.assertFalse(
                any(
                    imported == forbidden or imported.startswith(f"{forbidden}.")
                    for imported in imports
                ),
                msg=f"unexpected geometry dependency found in {sorted(imports)!r}",
            )

    def test_builder_has_no_scene_graph_dependency(self):
        try:
            module = importlib.import_module("domain.wall_placement_builder")
        except ModuleNotFoundError:
            self.fail("Missing contract target: domain.wall_placement_builder")

        imports = _imported_modules(module)
        for forbidden in ("scene_graph", "scenegraph"):
            self.assertFalse(
                any(
                    imported == forbidden or imported.startswith(f"{forbidden}.")
                    for imported in imports
                ),
                msg=f"unexpected scene graph dependency found in {sorted(imports)!r}",
            )

    def test_builder_has_no_manufacturing_dependency(self):
        try:
            module = importlib.import_module("domain.wall_placement_builder")
        except ModuleNotFoundError:
            self.fail("Missing contract target: domain.wall_placement_builder")

        imports = _imported_modules(module)
        for forbidden in ("manufacturing", "cnc", "cost", "commercial"):
            self.assertFalse(
                any(
                    imported == forbidden or imported.startswith(f"{forbidden}.")
                    for imported in imports
                ),
                msg=f"unexpected manufacturing dependency found in {sorted(imports)!r}",
            )

    def test_builder_has_no_freecad_dependency(self):
        try:
            module = importlib.import_module("domain.wall_placement_builder")
        except ModuleNotFoundError:
            self.fail("Missing contract target: domain.wall_placement_builder")

        imports = _imported_modules(module)
        for forbidden in ("freecad", "freecadgui", "part", "draft"):
            self.assertFalse(
                any(
                    imported == forbidden or imported.startswith(f"{forbidden}.")
                    for imported in imports
                ),
                msg=f"unexpected FreeCAD dependency found in {sorted(imports)!r}",
            )


if __name__ == "__main__":
    unittest.main()
