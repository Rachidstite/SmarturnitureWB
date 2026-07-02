import ast
import importlib
import inspect
import unittest

from domain.wall_cabinet_construction_mapper import (
    build_wall_cabinet_construction_model,
)
from domain.wall_cabinet_engineering_model import WallCabinetEngineeringModel
from domain.wall_cabinet_specification import WallCabinetSpecification
from domain.wall_placement_builder import build_wall_placements


def _read(subject, key):
    if isinstance(subject, dict):
        return subject[key]
    return getattr(subject, key)


class TestWallPanelGeometryContract(unittest.TestCase):
    def setUp(self):
        specification = WallCabinetSpecification(
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
        engineering_model = WallCabinetEngineeringModel(specification=specification)
        construction_model = build_wall_cabinet_construction_model(specification)
        self.placements = build_wall_placements(engineering_model, construction_model)

    def _build_wall_panel_geometry(self):
        try:
            module = importlib.import_module("engine.wall_panel_geometry")
        except ModuleNotFoundError:
            self.fail(
                "Missing contract target: expected module "
                "'engine.wall_panel_geometry' exposing "
                "'build_wall_panel_geometry(placements)'."
            )

        build_fn = getattr(module, "build_wall_panel_geometry", None)
        if not callable(build_fn):
            self.fail(
                "Missing contract target: expected callable "
                "'engine.wall_panel_geometry.build_wall_panel_geometry'."
            )
        return build_fn(self.placements)

    def test_builder_exposes_wall_panel_geometry_entrypoint(self):
        try:
            module = importlib.import_module("engine.wall_panel_geometry")
        except ModuleNotFoundError:
            self.fail("Missing contract target: engine.wall_panel_geometry")

        build_fn = getattr(module, "build_wall_panel_geometry", None)
        if not callable(build_fn):
            self.fail(
                "Missing contract target: expected callable "
                "'engine.wall_panel_geometry.build_wall_panel_geometry'."
            )

        signature = inspect.signature(build_fn)
        self.assertEqual(list(signature.parameters), ["placements"])

    def test_only_carcass_panels_are_generated(self):
        geometry = tuple(self._build_wall_panel_geometry())
        roles = {_read(item, "role") for item in geometry}
        self.assertEqual(
            roles,
            {
                "SIDE_PANEL",
                "TOP_PANEL",
                "BOTTOM_PANEL",
                "BACK_PANEL",
            },
        )

    def test_exactly_five_geometry_outputs_exist(self):
        geometry = tuple(self._build_wall_panel_geometry())
        self.assertEqual(len(geometry), 5)

    def test_every_output_corresponds_to_one_placement(self):
        geometry = tuple(self._build_wall_panel_geometry())
        placement_keys = tuple(_read(self.placements, "ordered_panel_keys"))
        seen_keys = []

        for item in geometry:
            placement_key = _read(item, "placement_key")
            self.assertIn(placement_key, placement_keys)
            seen_keys.append(placement_key)

        self.assertEqual(tuple(seen_keys), placement_keys)

    def test_panel_ordering_is_deterministic(self):
        first = tuple(self._build_wall_panel_geometry())
        second = tuple(self._build_wall_panel_geometry())
        self.assertEqual(first, second)

    def test_geometry_dimensions_match_placement_dimensions(self):
        geometry = tuple(self._build_wall_panel_geometry())
        for item in geometry:
            placement = _read(self.placements, _read(item, "placement_key"))
            self.assertEqual(_read(item, "width_mm"), _read(placement, "width_mm"))
            self.assertEqual(_read(item, "depth_mm"), _read(placement, "depth_mm"))
            self.assertEqual(_read(item, "height_mm"), _read(placement, "height_mm"))

    def test_geometry_origin_matches_placement_origin(self):
        geometry = tuple(self._build_wall_panel_geometry())
        for item in geometry:
            placement = _read(self.placements, _read(item, "placement_key"))
            self.assertEqual(_read(item, "origin_mm"), _read(placement, "position_mm"))

    def test_geometry_does_not_mutate_placements(self):
        before = self.placements
        self._build_wall_panel_geometry()
        self.assertEqual(self.placements, before)

    def test_geometry_generation_is_deterministic(self):
        first = self._build_wall_panel_geometry()
        second = self._build_wall_panel_geometry()
        self.assertEqual(first, second)

    def test_no_scene_graph_generation_or_rendering_contract(self):
        geometry = tuple(self._build_wall_panel_geometry())
        for item in geometry:
            for forbidden in (
                "scene_graph",
                "graph",
                "rendered_object",
                "freecad_object",
                "document_object",
            ):
                if isinstance(item, dict):
                    self.assertNotIn(forbidden, item)
                else:
                    self.assertFalse(hasattr(item, forbidden))

    def test_no_hardware_or_non_panel_components_contract(self):
        geometry = tuple(self._build_wall_panel_geometry())
        forbidden_roles = {
            "DOOR_PANEL",
            "SHELF",
            "DIVIDER",
            "DRAWER_BOX",
            "HINGE",
            "SLIDE",
            "HANDLE",
            "WALL_HARDWARE",
        }
        for item in geometry:
            self.assertNotIn(_read(item, "role"), forbidden_roles)


if __name__ == "__main__":
    unittest.main()
