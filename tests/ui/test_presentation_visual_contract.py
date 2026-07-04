# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Configurator V2
# Presentation Visual Contract Tests
#
# Verifies:
# - neutral state → neutral visual contract
# - selected state → stronger emphasis than neutral
# - hovered/focused → interaction emphasis
# - warning → warning outline intent
# - error → error outline intent
# - disabled → dim opacity
# - multiple states preserve dominant flag and severity
# - error dominant over warning
# - disabled visually distinct from selected/hovered
# - deterministic and side-effect free
# - no domain/manufacturing/cost/FreeCAD/Qt imports
# - no renderer/engine/workflow/event-bus naming
# ──────────────────────────────────────────────────────────────────────

from __future__ import annotations

import sys
import types
import unittest


class TestPresentationVisualContract(unittest.TestCase):
    """Verify the PresentationVisualContract resolver contract."""

    @classmethod
    def _import_vc_module(cls):
        """Import presentation modules directly, bypassing package __init__ chain."""
        import importlib.machinery
        import importlib.util

        # Clear stale entries
        for key in list(sys.modules):
            if key.startswith("ui.configurator_v2"):
                del sys.modules[key]

        # Pre-seed parent package
        parent = types.ModuleType("ui.configurator_v2")
        parent.__path__ = ["ui/configurator_v2"]
        sys.modules["ui.configurator_v2"] = parent

        # Load presentation_state first
        loader_ps = importlib.machinery.SourceFileLoader(
            "ui.configurator_v2.presentation_state",
            "ui/configurator_v2/presentation_state.py",
        )
        spec_ps = importlib.machinery.ModuleSpec(
            "ui.configurator_v2.presentation_state",
            loader_ps,
            origin="ui/configurator_v2/presentation_state.py",
        )
        ps_mod = importlib.util.module_from_spec(spec_ps)
        sys.modules["ui.configurator_v2.presentation_state"] = ps_mod
        loader_ps.exec_module(ps_mod)

        # Load presentation_visual_contract (depends on presentation_state)
        loader_vc = importlib.machinery.SourceFileLoader(
            "ui.configurator_v2.presentation_visual_contract",
            "ui/configurator_v2/presentation_visual_contract.py",
        )
        spec_vc = importlib.machinery.ModuleSpec(
            "ui.configurator_v2.presentation_visual_contract",
            loader_vc,
            origin="ui/configurator_v2/presentation_visual_contract.py",
        )
        vc_mod = importlib.util.module_from_spec(spec_vc)
        sys.modules["ui.configurator_v2.presentation_visual_contract"] = vc_mod
        loader_vc.exec_module(vc_mod)

        return ps_mod, vc_mod

    # ── Rule 1: neutral state → neutral contract ──────────────────

    def test_neutral_state_maps_to_neutral_contract(self):
        """A neutral presentation state produces a neutral visual contract."""
        ps, vc = self._import_vc_module()

        neutral_state = ps.FurniturePresentationState()
        contract = vc.resolve_visual_contract(neutral_state)

        self.assertTrue(contract.is_neutral)
        self.assertEqual(contract.emphasis_level, vc.EMPHASIS_NONE)
        self.assertEqual(contract.outline_intent, vc.OUTLINE_NONE)
        self.assertEqual(contract.opacity_intent, vc.OPACITY_NORMAL)
        self.assertEqual(contract.interaction_priority, 0)

    def test_none_state_maps_to_neutral_contract(self):
        """None state produces a neutral visual contract."""
        _, vc = self._import_vc_module()
        contract = vc.resolve_visual_contract(None)
        self.assertTrue(contract.is_neutral)

    # ── Rule 2: selected → stronger emphasis ──────────────────────

    def test_selected_emphasis_greater_than_neutral(self):
        """Selected state maps to higher emphasis than neutral."""
        ps, vc = self._import_vc_module()

        neutral = vc.resolve_visual_contract(ps.FurniturePresentationState())
        selected = vc.resolve_visual_contract(
            ps.FurniturePresentationState(selected=True)
        )

        emphasis_order = {
            vc.EMPHASIS_NONE: 0,
            vc.EMPHASIS_LOW: 1,
            vc.EMPHASIS_MEDIUM: 2,
            vc.EMPHASIS_HIGH: 3,
            vc.EMPHASIS_CRITICAL: 4,
        }
        self.assertGreater(
            emphasis_order.get(selected.emphasis_level, 0),
            emphasis_order.get(neutral.emphasis_level, 0),
        )

    def test_selected_outline_intent(self):
        """Selected state maps to SELECTED outline."""
        ps, vc = self._import_vc_module()
        contract = vc.resolve_visual_contract(
            ps.FurniturePresentationState(selected=True)
        )
        self.assertEqual(contract.outline_intent, vc.OUTLINE_SELECTED)

    # ── Rule 3: hovered/focused → interaction emphasis ────────────

    def test_hovered_maps_to_interaction_emphasis(self):
        """Hovered state maps to HOVERED outline intent."""
        ps, vc = self._import_vc_module()
        contract = vc.resolve_visual_contract(
            ps.FurniturePresentationState(hovered=True)
        )
        self.assertEqual(contract.outline_intent, vc.OUTLINE_HOVERED)

    def test_focused_maps_to_interaction_emphasis(self):
        """Focused state maps to FOCUSED outline intent."""
        ps, vc = self._import_vc_module()
        contract = vc.resolve_visual_contract(
            ps.FurniturePresentationState(focused=True)
        )
        self.assertEqual(contract.outline_intent, vc.OUTLINE_FOCUSED)

    # ── Rule 4: warning → warning visual intent ───────────────────

    def test_warning_maps_to_warning_outline(self):
        """Warning state maps to WARNING outline intent."""
        ps, vc = self._import_vc_module()
        contract = vc.resolve_visual_contract(
            ps.FurniturePresentationState(warning=True)
        )
        self.assertEqual(contract.outline_intent, vc.OUTLINE_WARNING)
        self.assertEqual(contract.emphasis_level, vc.EMPHASIS_HIGH)

    # ── Rule 5: error → error visual intent ───────────────────────

    def test_error_maps_to_error_outline(self):
        """Error state maps to ERROR outline intent."""
        ps, vc = self._import_vc_module()
        contract = vc.resolve_visual_contract(
            ps.FurniturePresentationState(error=True)
        )
        self.assertEqual(contract.outline_intent, vc.OUTLINE_ERROR)
        self.assertEqual(contract.emphasis_level, vc.EMPHASIS_CRITICAL)

    # ── Rule 6: disabled → dim opacity ────────────────────────────

    def test_disabled_maps_to_dim_opacity(self):
        """Disabled state maps to DIM opacity intent."""
        ps, vc = self._import_vc_module()
        contract = vc.resolve_visual_contract(
            ps.FurniturePresentationState(disabled=True)
        )
        self.assertEqual(contract.opacity_intent, vc.OPACITY_DIM)
        self.assertEqual(contract.outline_intent, vc.OUTLINE_DISABLED)

    def test_muted_maps_to_dim_opacity(self):
        """Muted state maps to DIM opacity intent."""
        ps, vc = self._import_vc_module()
        contract = vc.resolve_visual_contract(
            ps.FurniturePresentationState(muted=True)
        )
        self.assertEqual(contract.opacity_intent, vc.OPACITY_DIM)

    # ── Rule 7: multiple states preserve dominant flag and severity ─

    def test_multiple_states_preserve_dominant_and_severity(self):
        """Multiple active flags result in correct dominant flag and severity."""
        ps, vc = self._import_vc_module()

        state = ps.FurniturePresentationState(
            selected=True, hovered=True, warning=True
        )
        contract = vc.resolve_visual_contract(state)

        self.assertEqual(contract.dominant_flag, "warning")
        self.assertGreater(contract.visual_severity, 0)
        self.assertEqual(contract.emphasis_level, vc.EMPHASIS_HIGH)
        self.assertEqual(contract.outline_intent, vc.OUTLINE_WARNING)

    # ── Rule 8: error dominant over warning ────────────────────────

    def test_error_dominant_over_warning_in_contract(self):
        """Error yields higher emphasis and severity than warning."""
        ps, vc = self._import_vc_module()

        error_ct = vc.resolve_visual_contract(
            ps.FurniturePresentationState(error=True)
        )
        warning_ct = vc.resolve_visual_contract(
            ps.FurniturePresentationState(warning=True)
        )

        self.assertGreater(
            error_ct.visual_severity, warning_ct.visual_severity
        )
        emphasis_order = {
            vc.EMPHASIS_NONE: 0,
            vc.EMPHASIS_LOW: 1,
            vc.EMPHASIS_MEDIUM: 2,
            vc.EMPHASIS_HIGH: 3,
            vc.EMPHASIS_CRITICAL: 4,
        }
        self.assertGreater(
            emphasis_order[error_ct.emphasis_level],
            emphasis_order[warning_ct.emphasis_level],
        )

    def test_error_and_warning_combined_uses_error(self):
        """When both error and warning present, contract uses error tokens."""
        ps, vc = self._import_vc_module()
        contract = vc.resolve_visual_contract(
            ps.FurniturePresentationState(warning=True, error=True)
        )
        self.assertEqual(contract.outline_intent, vc.OUTLINE_ERROR)
        self.assertEqual(contract.dominant_flag, "error")
        self.assertEqual(contract.emphasis_level, vc.EMPHASIS_CRITICAL)

    # ── Rule 9: disabled visually distinct from selected/hovered ───

    def test_disabled_distinct_from_selected(self):
        """Disabled produces DIM opacity while selected produces NORMAL."""
        ps, vc = self._import_vc_module()

        disabled_ct = vc.resolve_visual_contract(
            ps.FurniturePresentationState(disabled=True)
        )
        selected_ct = vc.resolve_visual_contract(
            ps.FurniturePresentationState(selected=True)
        )

        self.assertEqual(disabled_ct.opacity_intent, vc.OPACITY_DIM)
        self.assertEqual(selected_ct.opacity_intent, vc.OPACITY_NORMAL)
        self.assertNotEqual(disabled_ct.outline_intent, selected_ct.outline_intent)

    def test_disabled_distinct_from_hovered(self):
        """Disabled and hovered produce different outline intents."""
        ps, vc = self._import_vc_module()

        disabled_ct = vc.resolve_visual_contract(
            ps.FurniturePresentationState(disabled=True)
        )
        hovered_ct = vc.resolve_visual_contract(
            ps.FurniturePresentationState(hovered=True)
        )

        self.assertEqual(disabled_ct.outline_intent, vc.OUTLINE_DISABLED)
        self.assertEqual(hovered_ct.outline_intent, vc.OUTLINE_HOVERED)

    # ── Rule 10: deterministic ────────────────────────────────────

    def test_resolver_is_deterministic(self):
        """resolve_visual_contract produces same output for same input."""
        ps, vc = self._import_vc_module()

        state = ps.FurniturePresentationState(
            selected=True, hovered=True, error=True
        )
        results = [vc.resolve_visual_contract(state) for _ in range(5)]
        for i in range(1, len(results)):
            self.assertEqual(results[0], results[i])

    def test_batch_resolver_preserves_order(self):
        """resolve_visual_contracts preserves order and cardinality."""
        ps, vc = self._import_vc_module()

        states = (
            None,
            ps.FurniturePresentationState(selected=True),
            ps.FurniturePresentationState(error=True),
            ps.FurniturePresentationState(),
        )
        contracts = vc.resolve_visual_contracts(states)

        self.assertEqual(len(contracts), 4)
        self.assertTrue(contracts[0].is_neutral)
        self.assertEqual(contracts[1].outline_intent, vc.OUTLINE_SELECTED)
        self.assertEqual(contracts[2].outline_intent, vc.OUTLINE_ERROR)
        self.assertTrue(contracts[3].is_neutral)

    # ── Rule 11: no domain/manufacturing/cost/Qt/FreeCAD imports ──

    def test_no_domain_manufacturing_cost_imports(self):
        """Source file must not import domain modules."""
        with open("ui/configurator_v2/presentation_visual_contract.py") as f:
            source = f.read()

        # Only check import lines — not docstring prose that mentions FreeCAD etc.
        import_lines = [
            line for line in source.splitlines()
            if line.strip().startswith(("import ", "from "))
        ]
        import_text = "\n".join(import_lines)

        forbidden = [
            "domain.",
            "manufacturing.",
            "cost_intelligence.",
            "commercial_outputs.",
            "optimization.",
            "FreeCAD",
            "QtWidgets",
            "QtCore",
            "QtGui",
            "scene_projection",
            "visual_components",
            "interactive_components",
            "presentation_binding",
        ]
        for token in forbidden:
            self.assertNotIn(
                token,
                import_text,
                msg=f"presentation_visual_contract.py must not import '{token}'",
            )

    # ── Rule 12: no renderer/engine/workflow naming ───────────────

    def test_no_renderer_engine_workflow_naming(self):
        """No renderer/engine/workflow/event-bus naming in VisualContract."""
        _, vc = self._import_vc_module()

        resolver_names = [
            name
            for name in dir(vc)
            if any(token in name.lower() for token in ("render", "engine", "workflow", "event", "bus"))
        ]
        self.assertEqual(
            resolver_names,
            [],
            msg=f"Visual contract should not contain renderer/engine/workflow/event names: {resolver_names}",
        )

    def test_class_attributes_no_engine_patterns(self):
        """PresentationVisualContract must not have engine-like methods."""
        _, vc = self._import_vc_module()
        contract = vc.PresentationVisualContract()

        engine_attrs = {"start", "stop", "run", "process", "dispatch", "subscribe", "emit"}
        for attr in engine_attrs:
            self.assertFalse(
                hasattr(contract, attr),
                msg=f"PresentationVisualContract should not have method '{attr}'",
            )

    # ── Rule 13: type validation ──────────────────────────────────

    def test_emphasis_level_validation(self):
        """Invalid emphasis level raises TypeError."""
        _, vc = self._import_vc_module()
        with self.assertRaises(TypeError):
            vc.PresentationVisualContract(emphasis_level="INVALID")

    def test_outline_intent_validation(self):
        """Invalid outline intent raises TypeError."""
        _, vc = self._import_vc_module()
        with self.assertRaises(TypeError):
            vc.PresentationVisualContract(outline_intent="INVALID")

    def test_opacity_intent_validation(self):
        """Invalid opacity intent raises TypeError."""
        _, vc = self._import_vc_module()
        with self.assertRaises(TypeError):
            vc.PresentationVisualContract(opacity_intent="INVALID")

    def test_interaction_priority_validation(self):
        """Non-int interaction_priority raises TypeError."""
        _, vc = self._import_vc_module()
        with self.assertRaises(TypeError):
            vc.PresentationVisualContract(interaction_priority="high")  # type: ignore

    # ── Rule 14: descriptor pairs ─────────────────────────────────

    def test_descriptor_pairs_none(self):
        """visual_contract_descriptor_pairs(None) returns ()."""
        _, vc = self._import_vc_module()
        self.assertEqual(vc.visual_contract_descriptor_pairs(None), ())

    def test_descriptor_pairs_neutral(self):
        """visual_contract_descriptor_pairs(neutral) returns ()."""
        _, vc = self._import_vc_module()
        self.assertEqual(vc.visual_contract_descriptor_pairs(vc.PresentationVisualContract()), ())

    def test_descriptor_pairs_active(self):
        """Non-neutral contract yields descriptor pairs."""
        ps, vc = self._import_vc_module()
        contract = vc.resolve_visual_contract(
            ps.FurniturePresentationState(selected=True)
        )
        pairs = dict(vc.visual_contract_descriptor_pairs(contract))
        self.assertEqual(pairs.get("vc_emphasis"), vc.EMPHASIS_HIGH)
        self.assertEqual(pairs.get("vc_outline"), vc.OUTLINE_SELECTED)
        self.assertEqual(pairs.get("vc_priority"), "25")

    # ── Rule 15: opacity intent completeness ──────────────────────

    def test_opacity_intents_contain_all_values(self):
        """OPACITY_INTENTS contains NORMAL, DIM, HIDDEN."""
        _, vc = self._import_vc_module()
        self.assertIn(vc.OPACITY_NORMAL, vc.OPACITY_INTENTS)
        self.assertIn(vc.OPACITY_DIM, vc.OPACITY_INTENTS)
        self.assertIn(vc.OPACITY_HIDDEN, vc.OPACITY_INTENTS)

    # ── Rule 16: emphasis levels completeness ─────────────────────

    def test_emphasis_levels_contain_all_values(self):
        """EMPHASIS_LEVELS contains NONE, LOW, MEDIUM, HIGH, CRITICAL."""
        _, vc = self._import_vc_module()
        self.assertIn(vc.EMPHASIS_NONE, vc.EMPHASIS_LEVELS)
        self.assertIn(vc.EMPHASIS_LOW, vc.EMPHASIS_LEVELS)
        self.assertIn(vc.EMPHASIS_MEDIUM, vc.EMPHASIS_LEVELS)
        self.assertIn(vc.EMPHASIS_HIGH, vc.EMPHASIS_LEVELS)
        self.assertIn(vc.EMPHASIS_CRITICAL, vc.EMPHASIS_LEVELS)


if __name__ == "__main__":
    unittest.main()
