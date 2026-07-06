try:
    import FreeCAD as App, Part
except ImportError:  # pragma: no cover - test environment fallback
    App = None
    Part = None
from scene_graph.node import SceneNode
from shared.roles import NodeRole
from core.material_manager import MaterialManager
from manufacturing.panel_shape_processor import process_panel_shape
from scene_graph.metadata import EngineeringDrawerFaceMetadata, build_visual_metadata
class SceneRenderer:
    def __init__(self, doc, mat: MaterialManager, hw, groups: dict, cnc_engine=None, placements=None, panel_features=None):
        self.doc = doc; self.mat = mat; self.hw = hw; self.groups = groups; self.cnc_engine = cnc_engine
        self.placements = list(placements or [])
        self.panel_features = list(panel_features or [])

    @staticmethod
    def build_manufacturing_overlays(markers):
        return list(markers or [])

    @staticmethod
    def build_visual_overlays(visual_metadata):
        if visual_metadata is None:
            return []

        overlays = []
        overlays.extend(
            SceneRenderer._edge_band_overlays(
                getattr(visual_metadata, "edge_banding", ()) or ()
            )
        )
        overlays.extend(
            SceneRenderer._drill_hole_overlays(
                getattr(visual_metadata, "drill_holes", ()) or ()
            )
        )
        overlays.extend(
            SceneRenderer._groove_overlays(
                getattr(visual_metadata, "grooves", ()) or ()
            )
        )
        overlays.extend(
            SceneRenderer._hardware_marker_overlays(
                getattr(visual_metadata, "hardware_markers", ()) or ()
            )
        )
        # ── Minifix hole overlays (HFG-3A) ────────────────────
        overlays.extend(
            SceneRenderer._minifix_overlays(
                getattr(visual_metadata, "minifix_holes", ()) or ()
            )
        )
        # ── Confirmat hole overlays (HFG-3A) ──────────────────
        overlays.extend(
            SceneRenderer._confirmat_overlays(
                getattr(visual_metadata, "confirmat_holes", ()) or ()
            )
        )
        # ── Shelf pin hole overlays (HFG-3B) ─────────────────
        overlays.extend(
            SceneRenderer._shelf_pin_hole_overlays(
                getattr(visual_metadata, "shelf_pin_holes", ()) or ()
            )
        )
        # ── Drawer slide hole overlays (HFG-3B) ──────────────
        overlays.extend(
            SceneRenderer._drawer_slide_hole_overlays(
                getattr(visual_metadata, "drawer_slide_holes", ()) or ()
            )
        )
        # ── Hinge cup hole overlays (HFG-3C) ────────────────
        overlays.extend(
            SceneRenderer._hinge_cup_hole_overlays(
                getattr(visual_metadata, "hinge_cup_holes", ()) or ()
            )
        )
        # ── Hinge plate position overlays (HFG-3C) ──────────
        overlays.extend(
            SceneRenderer._hinge_plate_position_overlays(
                getattr(visual_metadata, "hinge_plate_positions", ()) or ()
            )
        )
        # ── Screw hole overlays (HFG-3D) ──────────────────────
        overlays.extend(
            SceneRenderer._screw_hole_overlays(
                getattr(visual_metadata, "screw_holes", ()) or ()
            )
        )
        return overlays

    @staticmethod
    def build_viewport_overlay_commands(overlays):
        commands = []
        for overlay in overlays or []:
            overlay_type = str(overlay.get("overlay_type", "") or "")
            if overlay_type == "edge_banding":
                command = SceneRenderer._edge_viewport_command(overlay)
            elif overlay_type == "drill_hole":
                command = SceneRenderer._drill_viewport_command(overlay)
            elif overlay_type == "groove":
                command = SceneRenderer._groove_viewport_command(overlay)
            elif overlay_type == "hardware_marker":
                command = SceneRenderer._hardware_viewport_command(overlay)
            elif overlay_type == "minifix_hole":
                command = SceneRenderer._minifix_viewport_command(overlay)
            elif overlay_type == "confirmat_hole":
                command = SceneRenderer._confirmat_viewport_command(overlay)
            elif overlay_type == "shelf_pin_hole":
                command = SceneRenderer._shelf_pin_viewport_command(overlay)
            elif overlay_type == "drawer_slide_hole":
                command = SceneRenderer._drawer_slide_viewport_command(overlay)
            elif overlay_type == "hinge_cup_hole":
                command = SceneRenderer._hinge_cup_viewport_command(overlay)
            elif overlay_type == "hinge_plate_position":
                command = SceneRenderer._hinge_plate_viewport_command(overlay)
            elif overlay_type == "screw_hole":
                command = SceneRenderer._screw_viewport_command(overlay)
            else:
                continue
            if command is not None:
                commands.append(command)
        return commands

    @staticmethod
    def resolve_visual_metadata(
        node,
        *,
        cnc_report=None,
        manufacturing_edge_report=None,
        hardware_bom=None,
        assembly_report=None,
    ):
        return build_visual_metadata(
            node,
            cnc_report=cnc_report,
            manufacturing_edge_report=manufacturing_edge_report,
            hardware_bom=hardware_bom,
            assembly_report=assembly_report,
        )

    @staticmethod
    def _edge_band_overlays(edge_banding):
        return [
            {
                "overlay_type": "edge_banding",
                "visual_type": "EDGE_MARKER",
                "side": str(getattr(item, "side", "") or ""),
                "banding": str(getattr(item, "banding", "") or ""),
                "label": str(getattr(item, "label", "") or ""),
            }
            for item in edge_banding
        ]

    @staticmethod
    def _drill_hole_overlays(drill_holes):
        return [
            {
                "overlay_type": "drill_hole",
                "visual_type": "CIRCLE",
                "panel_identity": str(getattr(item, "panel_identity", "") or ""),
                "face": str(getattr(item, "face", "") or ""),
                "x": float(getattr(item, "x", 0.0) or 0.0),
                "y": float(getattr(item, "y", 0.0) or 0.0),
                "z": float(getattr(item, "z", 0.0) or 0.0),
                "diameter": float(getattr(item, "diameter", 0.0) or 0.0),
                "depth": float(getattr(item, "depth", 0.0) or 0.0),
                "axis": str(getattr(item, "axis", "Z") or "Z"),
                "is_through": bool(getattr(item, "is_through", False)),
                "source_operation_reference": str(
                    getattr(item, "source_operation_reference", "") or ""
                ),
            }
            for item in drill_holes
        ]

    @staticmethod
    def _groove_overlays(grooves):
        return [
            {
                "overlay_type": "groove",
                "visual_type": "CENTERLINE",
                "panel_identity": str(getattr(item, "panel_identity", "") or ""),
                "face": str(getattr(item, "face", "") or ""),
                "depth": float(getattr(item, "depth", 0.0) or 0.0),
                "label": str(getattr(item, "label", "") or ""),
                "source_rule": str(getattr(item, "source_rule", "") or ""),
            }
            for item in grooves
        ]

    @staticmethod
    def _hardware_marker_overlays(hardware_markers):
        return [
            {
                "overlay_type": "hardware_marker",
                "visual_type": SceneRenderer._hardware_visual_type(item),
                "panel_identity": str(getattr(item, "panel_identity", "") or ""),
                "sku": str(getattr(item, "sku", "") or ""),
                "quantity": int(getattr(item, "quantity", 0) or 0),
                "hardware_category": str(getattr(item, "hardware_category", "") or ""),
                "label": str(getattr(item, "label", "") or ""),
                "component_reference": tuple(
                    getattr(item, "component_reference", ()) or ()
                ),
                "cabinet_reference": tuple(
                    getattr(item, "cabinet_reference", ()) or ()
                ),
                "source_operation_references": tuple(
                    getattr(item, "source_operation_references", ()) or ()
                ),
            }
            for item in hardware_markers
        ]

    @staticmethod
    def _minifix_overlays(minifix_holes):
        """Build overlays for minifix drilling positions.

        Each minifix hole is a DrillHoleVisual — the overlay reuses
        the same positional fields as drill_hole overlays but with
        a distinct overlay_type so the viewport can style it differently.
        """
        return [
            {
                "overlay_type": "minifix_hole",
                "visual_type": "MINIFIX_SYMBOL",
                "panel_identity": str(getattr(item, "panel_identity", "") or ""),
                "face": str(getattr(item, "face", "") or ""),
                "x": float(getattr(item, "x", 0.0) or 0.0),
                "y": float(getattr(item, "y", 0.0) or 0.0),
                "z": float(getattr(item, "z", 0.0) or 0.0),
                "diameter": float(getattr(item, "diameter", 0.0) or 0.0),
                "depth": float(getattr(item, "depth", 0.0) or 0.0),
                "axis": str(getattr(item, "axis", "Z") or "Z"),
                "is_through": bool(getattr(item, "is_through", False)),
                "source_operation_reference": str(
                    getattr(item, "source_operation_reference", "") or ""
                ),
            }
            for item in minifix_holes
        ]

    @staticmethod
    def _confirmat_overlays(confirmat_holes):
        """Build overlays for confirmat drilling positions.

        Each confirmat hole is a DrillHoleVisual — the overlay reuses
        the same positional fields as drill_hole overlays but with
        a distinct overlay_type so the viewport can style it differently.
        """
        return [
            {
                "overlay_type": "confirmat_hole",
                "visual_type": "CONFIRMAT_SYMBOL",
                "panel_identity": str(getattr(item, "panel_identity", "") or ""),
                "face": str(getattr(item, "face", "") or ""),
                "x": float(getattr(item, "x", 0.0) or 0.0),
                "y": float(getattr(item, "y", 0.0) or 0.0),
                "z": float(getattr(item, "z", 0.0) or 0.0),
                "diameter": float(getattr(item, "diameter", 0.0) or 0.0),
                "depth": float(getattr(item, "depth", 0.0) or 0.0),
                "axis": str(getattr(item, "axis", "Z") or "Z"),
                "is_through": bool(getattr(item, "is_through", False)),
                "source_operation_reference": str(
                    getattr(item, "source_operation_reference", "") or ""
                ),
            }
            for item in confirmat_holes
        ]

    @staticmethod
    def _shelf_pin_hole_overlays(shelf_pin_holes):
        """Build overlays for shelf pin drilling positions.

        Each shelf pin hole is a DrillHoleVisual — the overlay reuses
        the same positional fields as drill_hole overlays but with
        a distinct overlay_type so the viewport can style it differently.
        """
        return [
            {
                "overlay_type": "shelf_pin_hole",
                "visual_type": "SHELF_PIN_SYMBOL",
                "panel_identity": str(getattr(item, "panel_identity", "") or ""),
                "face": str(getattr(item, "face", "") or ""),
                "x": float(getattr(item, "x", 0.0) or 0.0),
                "y": float(getattr(item, "y", 0.0) or 0.0),
                "z": float(getattr(item, "z", 0.0) or 0.0),
                "diameter": float(getattr(item, "diameter", 0.0) or 0.0),
                "depth": float(getattr(item, "depth", 0.0) or 0.0),
                "axis": str(getattr(item, "axis", "Z") or "Z"),
                "is_through": bool(getattr(item, "is_through", False)),
                "source_operation_reference": str(
                    getattr(item, "source_operation_reference", "") or ""
                ),
            }
            for item in shelf_pin_holes
        ]

    @staticmethod
    def _drawer_slide_hole_overlays(drawer_slide_holes):
        """Build overlays for drawer slide hole drilling positions.

        Each drawer slide hole is a DrillHoleVisual — the overlay reuses
        the same positional fields as drill_hole overlays but with
        a distinct overlay_type so the viewport can style it differently.
        """
        return [
            {
                "overlay_type": "drawer_slide_hole",
                "visual_type": "DRAWER_SLIDE_SYMBOL",
                "panel_identity": str(getattr(item, "panel_identity", "") or ""),
                "face": str(getattr(item, "face", "") or ""),
                "x": float(getattr(item, "x", 0.0) or 0.0),
                "y": float(getattr(item, "y", 0.0) or 0.0),
                "z": float(getattr(item, "z", 0.0) or 0.0),
                "diameter": float(getattr(item, "diameter", 0.0) or 0.0),
                "depth": float(getattr(item, "depth", 0.0) or 0.0),
                "axis": str(getattr(item, "axis", "Z") or "Z"),
                "is_through": bool(getattr(item, "is_through", False)),
                "source_operation_reference": str(
                    getattr(item, "source_operation_reference", "") or ""
                ),
            }
            for item in drawer_slide_holes
        ]

    @staticmethod
    def _hinge_cup_hole_overlays(hinge_cup_holes):
        """Build overlays for hinge cup drilling positions.

        Each hinge cup hole is a DrillHoleVisual — the overlay reuses
        the same positional fields as drill_hole overlays but with
        a distinct overlay_type so the viewport can style it differently.
        """
        return [
            {
                "overlay_type": "hinge_cup_hole",
                "visual_type": "HINGE_CUP_SYMBOL",
                "panel_identity": str(getattr(item, "panel_identity", "") or ""),
                "face": str(getattr(item, "face", "") or ""),
                "x": float(getattr(item, "x", 0.0) or 0.0),
                "y": float(getattr(item, "y", 0.0) or 0.0),
                "z": float(getattr(item, "z", 0.0) or 0.0),
                "diameter": float(getattr(item, "diameter", 0.0) or 0.0),
                "depth": float(getattr(item, "depth", 0.0) or 0.0),
                "axis": str(getattr(item, "axis", "Z") or "Z"),
                "is_through": bool(getattr(item, "is_through", False)),
                "source_operation_reference": str(
                    getattr(item, "source_operation_reference", "") or ""
                ),
            }
            for item in hinge_cup_holes
        ]

    @staticmethod
    def _hinge_plate_position_overlays(hinge_plate_positions):
        """Build overlays for hinge plate drilling positions.

        Each hinge plate position is a DrillHoleVisual — the overlay reuses
        the same positional fields as drill_hole overlays but with
        a distinct overlay_type so the viewport can style it differently.
        """
        return [
            {
                "overlay_type": "hinge_plate_position",
                "visual_type": "HINGE_PLATE_SYMBOL",
                "panel_identity": str(getattr(item, "panel_identity", "") or ""),
                "face": str(getattr(item, "face", "") or ""),
                "x": float(getattr(item, "x", 0.0) or 0.0),
                "y": float(getattr(item, "y", 0.0) or 0.0),
                "z": float(getattr(item, "z", 0.0) or 0.0),
                "diameter": float(getattr(item, "diameter", 0.0) or 0.0),
                "depth": float(getattr(item, "depth", 0.0) or 0.0),
                "axis": str(getattr(item, "axis", "Z") or "Z"),
                "is_through": bool(getattr(item, "is_through", False)),
                "source_operation_reference": str(
                    getattr(item, "source_operation_reference", "") or ""
                ),
            }
            for item in hinge_plate_positions
        ]

    @staticmethod
    def _screw_hole_overlays(screw_holes):
        """Build overlays for screw drilling positions.

        Each screw hole is a DrillHoleVisual — the overlay reuses
        the same positional fields as drill_hole overlays but with
        a distinct overlay_type so the viewport can style it differently.
        """
        return [
            {
                "overlay_type": "screw_hole",
                "visual_type": "SCREW_SYMBOL",
                "panel_identity": str(getattr(item, "panel_identity", "") or ""),
                "face": str(getattr(item, "face", "") or ""),
                "x": float(getattr(item, "x", 0.0) or 0.0),
                "y": float(getattr(item, "y", 0.0) or 0.0),
                "z": float(getattr(item, "z", 0.0) or 0.0),
                "diameter": float(getattr(item, "diameter", 0.0) or 0.0),
                "depth": float(getattr(item, "depth", 0.0) or 0.0),
                "axis": str(getattr(item, "axis", "Z") or "Z"),
                "is_through": bool(getattr(item, "is_through", False)),
                "source_operation_reference": str(
                    getattr(item, "source_operation_reference", "") or ""
                ),
            }
            for item in screw_holes
        ]

    @staticmethod
    def _hardware_visual_type(item):
        category = str(getattr(item, "hardware_category", "") or "").upper()
        sku = str(getattr(item, "sku", "") or "").upper()
        text = " ".join(
            (
                category,
                sku,
                str(getattr(item, "label", "") or "").upper(),
            )
        )
        if "HINGE" in text:
            return "HINGE_SYMBOL"
        if "DRAWER_SLIDE" in text or "SLIDE" in text:
            return "DRAWER_SLIDE_SYMBOL"
        if "SHELF_PIN" in text or "SHELF PIN" in text:
            return "SHELF_PIN_SYMBOL"
        return "HARDWARE_SYMBOL"

    @staticmethod
    def _edge_viewport_command(overlay):
        return {
            "command_type": "edge_marker",
            "overlay_type": "edge_banding",
            "label": str(overlay.get("label", "") or ""),
            "side": str(overlay.get("side", "") or ""),
            "banding": str(overlay.get("banding", "") or ""),
            "position": None,
            "face": "",
            "source_reference": "",
        }

    @staticmethod
    def _drill_viewport_command(overlay):
        return SceneRenderer._decorate_hole_command({
            "command_type": "circle_marker",
            "overlay_type": "drill_hole",
            "label": str(overlay.get("label", "") or "Drill hole"),
            "position": (
                float(overlay.get("x", 0.0) or 0.0),
                float(overlay.get("y", 0.0) or 0.0),
                float(overlay.get("z", 0.0) or 0.0),
            ),
            "face": str(overlay.get("face", "") or ""),
            "diameter": float(overlay.get("diameter", 0.0) or 0.0),
            "size": float(overlay.get("diameter", 0.0) or 0.0),
            "source_reference": str(overlay.get("source_operation_reference", "") or ""),
            "panel_identity": str(overlay.get("panel_identity", "") or ""),
        }, overlay)

    @staticmethod
    def _groove_viewport_command(overlay):
        face = str(overlay.get("face", "") or "")
        source_rule = str(overlay.get("source_rule", "") or "")
        if not face and not source_rule:
            return None
        return {
            "command_type": "centerline_marker",
            "overlay_type": "groove",
            "label": str(overlay.get("label", "") or ""),
            "position": None,
            "face": face,
            "depth": float(overlay.get("depth", 0.0) or 0.0),
            "size": float(overlay.get("depth", 0.0) or 0.0),
            "source_reference": source_rule,
            "panel_identity": str(overlay.get("panel_identity", "") or ""),
        }

    @staticmethod
    def _hardware_viewport_command(overlay):
        return {
            "command_type": "symbolic_marker",
            "overlay_type": "hardware_marker",
            "label": str(overlay.get("label", "") or overlay.get("sku", "") or ""),
            "symbol": str(overlay.get("visual_type", "") or "HARDWARE_SYMBOL"),
            "position": None,
            "face": "",
            "size": int(overlay.get("quantity", 0) or 0),
            "source_reference": tuple(
                overlay.get("source_operation_references", ()) or ()
            ),
            "panel_identity": str(overlay.get("panel_identity", "") or ""),
            "sku": str(overlay.get("sku", "") or ""),
        }

    @staticmethod
    def _minifix_viewport_command(overlay):
        """Build a viewport command for a minifix hole overlay.

        Reuses circle_marker command_type (same as drill_hole) but
        with overlay_type=minifix_hole so the viewport can render
        it with a distinct visual style (e.g. larger diameter marker,
        different colour).
        """
        return SceneRenderer._decorate_hole_command({
            "command_type": "circle_marker",
            "overlay_type": "minifix_hole",
            "label": str(overlay.get("label", "") or "Minifix hole"),
            "position": (
                float(overlay.get("x", 0.0) or 0.0),
                float(overlay.get("y", 0.0) or 0.0),
                float(overlay.get("z", 0.0) or 0.0),
            ),
            "face": str(overlay.get("face", "") or ""),
            "diameter": float(overlay.get("diameter", 0.0) or 0.0),
            "size": float(overlay.get("diameter", 0.0) or 0.0),
            "source_reference": str(
                overlay.get("source_operation_reference", "") or ""
            ),
            "panel_identity": str(overlay.get("panel_identity", "") or ""),
        }, overlay)

    @staticmethod
    def _confirmat_viewport_command(overlay):
        """Build a viewport command for a confirmat hole overlay.

        Reuses circle_marker command_type (same as drill_hole) but
        with overlay_type=confirmat_hole so the viewport can render
        it with a distinct visual style.
        """
        return SceneRenderer._decorate_hole_command({
            "command_type": "circle_marker",
            "overlay_type": "confirmat_hole",
            "label": str(overlay.get("label", "") or "Confirmat hole"),
            "position": (
                float(overlay.get("x", 0.0) or 0.0),
                float(overlay.get("y", 0.0) or 0.0),
                float(overlay.get("z", 0.0) or 0.0),
            ),
            "face": str(overlay.get("face", "") or ""),
            "diameter": float(overlay.get("diameter", 0.0) or 0.0),
            "size": float(overlay.get("diameter", 0.0) or 0.0),
            "source_reference": str(
                overlay.get("source_operation_reference", "") or ""
            ),
            "panel_identity": str(overlay.get("panel_identity", "") or ""),
        }, overlay)

    @staticmethod
    def _shelf_pin_viewport_command(overlay):
        """Build a viewport command for a shelf pin hole overlay.

        Reuses circle_marker command_type with overlay_type=shelf_pin_hole
        so the viewport can render it with a distinct visual style
        (e.g. small diameter marker, different colour).
        """
        return SceneRenderer._decorate_hole_command({
            "command_type": "circle_marker",
            "overlay_type": "shelf_pin_hole",
            "label": str(overlay.get("label", "") or "Shelf pin hole"),
            "position": (
                float(overlay.get("x", 0.0) or 0.0),
                float(overlay.get("y", 0.0) or 0.0),
                float(overlay.get("z", 0.0) or 0.0),
            ),
            "face": str(overlay.get("face", "") or ""),
            "diameter": float(overlay.get("diameter", 0.0) or 0.0),
            "size": float(overlay.get("diameter", 0.0) or 0.0),
            "source_reference": str(
                overlay.get("source_operation_reference", "") or ""
            ),
            "panel_identity": str(overlay.get("panel_identity", "") or ""),
        }, overlay)

    @staticmethod
    def _drawer_slide_viewport_command(overlay):
        """Build a viewport command for a drawer slide hole overlay.

        Reuses circle_marker command_type with overlay_type=drawer_slide_hole
        so the viewport can render it with a distinct visual style.
        """
        return SceneRenderer._decorate_hole_command({
            "command_type": "circle_marker",
            "overlay_type": "drawer_slide_hole",
            "label": str(overlay.get("label", "") or "Drawer slide hole"),
            "position": (
                float(overlay.get("x", 0.0) or 0.0),
                float(overlay.get("y", 0.0) or 0.0),
                float(overlay.get("z", 0.0) or 0.0),
            ),
            "face": str(overlay.get("face", "") or ""),
            "diameter": float(overlay.get("diameter", 0.0) or 0.0),
            "size": float(overlay.get("diameter", 0.0) or 0.0),
            "source_reference": str(
                overlay.get("source_operation_reference", "") or ""
            ),
            "panel_identity": str(overlay.get("panel_identity", "") or ""),
        }, overlay)

    @staticmethod
    def _hinge_cup_viewport_command(overlay):
        """Build a viewport command for a hinge cup hole overlay.

        Reuses circle_marker command_type with overlay_type=hinge_cup_hole
        so the viewport can render it with a distinct visual style
        (e.g. larger diameter marker for 35mm cup holes).
        """
        return SceneRenderer._decorate_hole_command({
            "command_type": "circle_marker",
            "overlay_type": "hinge_cup_hole",
            "label": str(overlay.get("label", "") or "Hinge cup hole"),
            "position": (
                float(overlay.get("x", 0.0) or 0.0),
                float(overlay.get("y", 0.0) or 0.0),
                float(overlay.get("z", 0.0) or 0.0),
            ),
            "face": str(overlay.get("face", "") or ""),
            "diameter": float(overlay.get("diameter", 0.0) or 0.0),
            "size": float(overlay.get("diameter", 0.0) or 0.0),
            "source_reference": str(
                overlay.get("source_operation_reference", "") or ""
            ),
            "panel_identity": str(overlay.get("panel_identity", "") or ""),
        }, overlay)

    @staticmethod
    def _hinge_plate_viewport_command(overlay):
        """Build a viewport command for a hinge plate position overlay.

        Reuses circle_marker command_type with overlay_type=hinge_plate_position
        so the viewport can render it with a distinct visual style.
        """
        return {
            "command_type": "circle_marker",
            "overlay_type": "hinge_plate_position",
            "label": str(overlay.get("label", "") or "Hinge plate position"),
            "position": (
                float(overlay.get("x", 0.0) or 0.0),
                float(overlay.get("y", 0.0) or 0.0),
                float(overlay.get("z", 0.0) or 0.0),
            ),
            "face": str(overlay.get("face", "") or ""),
            "diameter": float(overlay.get("diameter", 0.0) or 0.0),
            "size": float(overlay.get("diameter", 0.0) or 0.0),
            "source_reference": str(
                overlay.get("source_operation_reference", "") or ""
            ),
            "panel_identity": str(overlay.get("panel_identity", "") or ""),
        }

    @staticmethod
    def _screw_viewport_command(overlay):
        """Build a viewport command for a screw hole overlay.

        Reuses circle_marker command_type with overlay_type=screw_hole
        so the viewport can render it with a distinct visual style.
        """
        return SceneRenderer._decorate_hole_command({
            "command_type": "circle_marker",
            "overlay_type": "screw_hole",
            "label": str(overlay.get("label", "") or "Screw hole"),
            "position": (
                float(overlay.get("x", 0.0) or 0.0),
                float(overlay.get("y", 0.0) or 0.0),
                float(overlay.get("z", 0.0) or 0.0),
            ),
            "face": str(overlay.get("face", "") or ""),
            "diameter": float(overlay.get("diameter", 0.0) or 0.0),
            "size": float(overlay.get("diameter", 0.0) or 0.0),
            "source_reference": str(
                overlay.get("source_operation_reference", "") or ""
            ),
            "panel_identity": str(overlay.get("panel_identity", "") or ""),
        }, overlay)

    @staticmethod
    def _resolve_hole_style(overlay_type: str, overlay: dict) -> str:
        """Infer a high-fidelity hole style from existing overlay data.

        Returns one of:
          - 'through'   — hole passes entirely through the panel
          - 'blind'     — hole has a defined depth, does not pass through
          - 'cup'       — large-diameter hinge cup bore (hinge_cup_hole)
          - 'pilot'     — small-diameter pilot/screw hole (screw_hole)

        This is a rendering-only inference from existing overlay metadata.
        No manufacturing logic, no reclassification of hardware_intent.
        The overlay_type and is_through field are consumed directly from
        the overlay dict that SceneRenderer already produced.
        """
        # Cup holes are always cup style regardless of is_through
        if overlay_type in ("hinge_cup_hole",):
            return "cup"
        # Screw/pilot holes are always pilot style
        if overlay_type in ("screw_hole",):
            return "pilot"
        # All other holes: use is_through if available
        is_through = bool(overlay.get("is_through", False))
        return "through" if is_through else "blind"

    @staticmethod
    def _resolve_drill_direction(face: str) -> str:
        """Normalize a panel-face string into a stable drill-direction value.

        Returns one of: front, back, left, right, top, bottom, unknown.
        """
        normalized = str(face).strip().upper() if face else ""
        mapping = {
            "FRONT": "front",
            "BACK": "back",
            "LEFT": "left",
            "RIGHT": "right",
            "TOP": "top",
            "BOTTOM": "bottom",
        }
        return mapping.get(normalized, "unknown")

    @staticmethod
    def _resolve_hole_depth(overlay: dict) -> tuple[float, str]:
        """Resolve hole depth metadata from an overlay dict.

        Returns (hole_depth, hole_depth_mode) where:
          - (0.0, "through")     — is_through is truthy
          - (depth, "blind")     — positive numeric depth
          - (0.0, "unspecified") — no depth, invalid depth, or negative depth

        This is a rendering-only inference.  No estimation from diameter,
        no use of panel thickness.
        """
        if bool(overlay.get("is_through", False)):
            return (0.0, "through")
        try:
            raw = overlay.get("depth", None)
            if raw is None:
                return (0.0, "unspecified")
            depth = float(raw)
            if depth > 0:
                return (depth, "blind")
            return (0.0, "unspecified")
        except (ValueError, TypeError):
            return (0.0, "unspecified")

    @staticmethod
    def _decorate_hole_command(command: dict, overlay: dict | None = None) -> dict:
        """Add hole_style, drill_direction, hole_depth, and hole_depth_mode
        decoration to a hole viewport command in-place.

        Reads command["overlay_type"], resolves the hole style via
        _resolve_hole_style, and sets command["hole_style"].
        Resolves drill_direction from the face field and sets
        command["drill_direction"].
        Resolves depth metadata via _resolve_hole_depth and sets
        command["hole_depth"] and command["hole_depth_mode"].

        When *overlay* is provided (the source overlay dict), it is used
        as the source for fields like is_through, face, and depth. Falls
        back to command when overlay is None for backward compatibility.

        Returns the same dict for convenience (fluent / return-value wrapping).
        """
        overlay_type = str(command.get("overlay_type", "") or "")
        source = overlay if overlay is not None else command
        command["hole_style"] = SceneRenderer._resolve_hole_style(
            overlay_type, source
        )
        face = str((overlay if overlay is not None else command).get("face", "") or "")
        command["drill_direction"] = SceneRenderer._resolve_drill_direction(face)
        hole_depth, hole_depth_mode = SceneRenderer._resolve_hole_depth(source)
        command["hole_depth"] = hole_depth
        command["hole_depth_mode"] = hole_depth_mode
        return command

    def render(self, node: SceneNode):
        # استخدام الـ Registry
        from scene_graph.registry import RendererRegistry
        RendererRegistry.render(node, self)

    def render_graph(self, scene_graph):
        nodes = scene_graph.all_nodes()

        print("[TOTAL NODES]", len(nodes))

        for node in nodes:
            print("[NODE]", node.role, node.identity.key)
            self.render(node)

    def _ensure_group(self, group_name):
        if group_name not in self.groups:
            self.groups[group_name] = self.doc.addObject("App::DocumentObjectGroup", group_name)

    def hinge_offsets_for(self, door_id):
        offsets = []
        for placement in self.placements:
            if getattr(placement, "hardware_intent", None) != "INTENT_HINGE":
                continue
            if (
                getattr(placement, "host_node_id", None) != door_id
                and getattr(placement, "target_node_id", None) != door_id
            ):
                continue
            anchor = getattr(placement, "anchor", None)
            if anchor is None:
                continue
            offsets.append(anchor.offset_y)
        return sorted(offsets)

    def _render_simple_panel(self, node: SceneNode):
        print("[RENDER PANEL]", node.role, node.identity.key)
        """رسم افتراضي لأي لوح."""
        self._ensure_group(node.group)
        name = node.identity.key
        obj = self.doc.addObject("Part::Feature", name)
        base_shape = Part.makeBox(node.width, node.depth, node.height)
        if node.role in (
            NodeRole.BACK_PANEL,
            NodeRole.SIDE_PANEL,
            NodeRole.TOP_PANEL,
            NodeRole.BOTTOM_PANEL,
            NodeRole.DIVIDER,
        ):
            obj.Shape = process_panel_shape(
                base_shape,
                node,
                self.panel_features,
                panel_origin=(node.x, node.y, node.z),
            )
        else:
            obj.Shape = base_shape
        obj.Placement = App.Placement(App.Vector(node.x, node.y, node.z), App.Rotation())
        obj.ViewObject.ShapeColor = self._visual_color_for(node)
        try:
            if node.role == NodeRole.BACK_PANEL:
                obj.ViewObject.Transparency = 35
            elif node.role == NodeRole.DIVIDER:
                obj.ViewObject.Transparency = 15
        except Exception:
            pass
        obj.addProperty("App::PropertyString", "SmartUUID")
        obj.SmartUUID = name
        self.groups[node.group].addObject(obj)

    @staticmethod
    def _visual_color_for(node: SceneNode):
        role_name = getattr(getattr(node, "role", None), "name", str(getattr(node, "role", None)))
        if role_name == "SIDE_PANEL":
            return (0.68, 0.49, 0.31)
        if role_name == "TOP_PANEL":
            return (0.75, 0.57, 0.36)
        if role_name == "BOTTOM_PANEL":
            return (0.72, 0.54, 0.34)
        if role_name == "BACK_PANEL":
            return (0.84, 0.85, 0.87)
        if role_name == "SHELF":
            return (0.90, 0.81, 0.62)
        if role_name == "DIVIDER":
            return (0.74, 0.57, 0.37)
        if role_name == "DRAWER_FACE":
            return (0.76, 0.64, 0.46)
        if role_name == "DOOR_PANEL":
            return (0.58, 0.41, 0.25)
        colors = {
            "Shelves": (0.90, 0.81, 0.62),
            "Drawers": (0.76, 0.64, 0.46),
            "Doors": (0.58, 0.41, 0.25),
            "Dividers": (0.74, 0.57, 0.37),
            "Carcass": (0.68, 0.49, 0.31),
        }
        return colors.get(getattr(node, "group", None), (0.68, 0.49, 0.31))

# --- تسجيل الاستراتيجيات ---
from scene_graph.registry import RendererRegistry

def _drawer_strategy(node, renderer):
    meta = node.metadata
    renderer._ensure_group(node.group)
    if isinstance(meta, EngineeringDrawerFaceMetadata) or getattr(
        meta,
        "source_rule",
        "",
    ) == "resolved_drawer_face_projection":
        renderer._render_simple_panel(node)
        return

    from builders.drawer_builder import DrawerBuilder

    DrawerBuilder.build(
        renderer.doc, renderer.groups[node.group], node.identity.key,
        node.width, node.height,  # face_w, face_h
        node.x, node.y, node.z,
        meta.box_w, meta.box_h, meta.box_d,
        meta.box_x, meta.box_y, meta.box_z,
        renderer.mat, meta.bottom_thickness
    )

def _door_strategy(node, renderer):
    from builders.door_builder import DoorBuilder

    meta = node.metadata
    renderer._ensure_group(node.group)
    door_type_str = meta.door_type.replace("_", " ").title()
    cnc = renderer.cnc_engine if meta.cnc_enabled else None
    hw_b = renderer.hw
    door_obj = DoorBuilder.build(
        renderer.doc, renderer.groups[node.group], node.identity.key,
        node.width, node.height,
        node.x, node.y, node.z,
        renderer.mat, door_type_str,
        cnc, hw_b, renderer.groups.get("Hardware"),
        meta.hinge_side,
        meta.layer,
        hinge_offsets=renderer.hinge_offsets_for(node.identity.key) or None
    )

    if door_obj is not None and hasattr(door_obj, "Shape") and renderer.panel_features:
        processed_shape = process_panel_shape(
            door_obj.Shape,
            node,
            renderer.panel_features,
            panel_origin=(node.x, node.y, node.z),
        )
        if processed_shape is not None:
            door_obj.Shape = processed_shape

def _shelf_strategy(node, renderer):
    renderer._render_simple_panel(node)

def _divider_strategy(node, renderer):
    renderer._render_simple_panel(node)

RendererRegistry.register(NodeRole.SHELF, _shelf_strategy)
RendererRegistry.register(NodeRole.DIVIDER, _divider_strategy)
RendererRegistry.register(NodeRole.DRAWER_FACE, _drawer_strategy)
RendererRegistry.register(NodeRole.DOOR_PANEL, _door_strategy)
# باقي الأدوار تستخدم _render_simple_panel افتراضياً
