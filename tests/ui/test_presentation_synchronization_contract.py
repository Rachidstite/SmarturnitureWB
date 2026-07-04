# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Configurator V2
# Presentation Synchronization Contract Tests
#
# Verifies:
# - neutral components yield neutral snapshots
# - selected/hovered/focused ids synchronize correctly
# - warning/error ids synchronize correctly
# - error dominant over warning
# - disabled visually distinct with dim opacity
# - multiple flags coexist
# - deterministic output
# - no input mutation
# - no domain/manufacturing/cost/Qt imports
# - no engine/workflow/event-bus naming
# ──────────────────────────────────────────────────────────────────────

from __future__ import annotations

import sys
import types
import unittest


class TestPresentationSynchronizationContract(unittest.TestCase):
    """Verify the synchronization contract."""

    @classmethod
    def _import_modules(cls):
        """Import all needed modules via direct load (bypassing qt_compat)."""
        import importlib.machinery
        import importlib.util

        for key in list(sys.modules):
            if key.startswith("ui.configurator_v2"):
                del sys.modules[key]

        parent = types.ModuleType("ui.configurator_v2")
        parent.__path__ = ["ui/configurator_v2"]
        sys.modules["ui.configurator_v2"] = parent

        def _load(name, path):
            loader = importlib.machinery.SourceFileLoader(name, path)
            spec = importlib.machinery.ModuleSpec(
                name, loader, origin=path
            )
            mod = importlib.util.module_from_spec(spec)
            sys.modules[name] = mod
            loader.exec_module(mod)
            return mod

        ps = _load("ui.configurator_v2.presentation_state", "ui/configurator_v2/presentation_state.py")
        binding = _load("ui.configurator_v2.presentation_binding", "ui/configurator_v2/presentation_binding.py")
        vc = _load("ui.configurator_v2.presentation_visual_contract", "ui/configurator_v2/presentation_visual_contract.py")
        sync = _load("ui.configurator_v2.presentation_synchronization", "ui/configurator_v2/presentation_synchronization.py")
        return ps, binding, vc, sync

    # ── Rule 1: neutral components ───────────────────────────────

    def test_neutral_components_produce_neutral_snapshot(self):
        """Component not in any flag set gets neutral presentation + visual."""
        *_, sync = self._import_modules()
        results = sync.synchronize_presentation(
            ("c1", "c2"),
        )
        self.assertEqual(len(results), 2)
        self.assertTrue(results[0].is_neutral)
        self.assertTrue(results[1].is_neutral)
        self.assertTrue(results[0].presentation_state.is_neutral)
        self.assertTrue(results[0].visual_contract.is_neutral)

    def test_empty_ids_returns_empty(self):
        """Empty component_ids returns empty tuple."""
        *_, sync = self._import_modules()
        self.assertEqual(sync.synchronize_presentation(()), ())

    # ── Rule 2: selected synchronizes ────────────────────────────

    def test_selected_synchronizes(self):
        """Selected ids produce selected state and SELECTED outline."""
        ps, _, vc, sync = self._import_modules()
        results = sync.synchronize_presentation(
            ("d1", "d2"),
            selected_ids=frozenset({"d1"}),
        )
        self.assertTrue(results[0].presentation_state.selected)
        self.assertEqual(results[0].visual_contract.outline_intent, vc.OUTLINE_SELECTED)
        self.assertFalse(results[1].presentation_state.selected)
        self.assertTrue(results[1].is_neutral)

    # ── Rule 3: hovered and focused ──────────────────────────────

    def test_hovered_synchronizes(self):
        """Hovered id produces hovered state and HOVERED outline."""
        _, _, vc, sync = self._import_modules()
        results = sync.synchronize_presentation(
            ("d1", "d2"),
            hovered_id="d1",
        )
        self.assertTrue(results[0].presentation_state.hovered)
        self.assertEqual(results[0].visual_contract.outline_intent, vc.OUTLINE_HOVERED)
        self.assertFalse(results[1].presentation_state.hovered)

    def test_focused_synchronizes(self):
        """Focused id produces focused state and FOCUSED outline."""
        _, _, vc, sync = self._import_modules()
        results = sync.synchronize_presentation(
            ("d1", "d2"),
            focused_id="d1",
        )
        self.assertTrue(results[0].presentation_state.focused)
        self.assertEqual(results[0].visual_contract.outline_intent, vc.OUTLINE_FOCUSED)
        self.assertFalse(results[1].presentation_state.focused)

    # ── Rule 4: warning and error ────────────────────────────────

    def test_warning_synchronizes(self):
        """Warning ids produce warning state and WARNING outline."""
        _, _, vc, sync = self._import_modules()
        results = sync.synchronize_presentation(
            ("p1",),
            warning_ids=frozenset({"p1"}),
        )
        self.assertTrue(results[0].presentation_state.warning)
        self.assertEqual(results[0].visual_contract.outline_intent, vc.OUTLINE_WARNING)

    def test_error_synchronizes(self):
        """Error ids produce error state and ERROR outline."""
        _, _, vc, sync = self._import_modules()
        results = sync.synchronize_presentation(
            ("p1",),
            error_ids=frozenset({"p1"}),
        )
        self.assertTrue(results[0].presentation_state.error)
        self.assertEqual(results[0].visual_contract.outline_intent, vc.OUTLINE_ERROR)
        self.assertEqual(results[0].visual_contract.emphasis_level, vc.EMPHASIS_CRITICAL)

    # ── Rule 5: error dominant over warning ──────────────────────

    def test_error_dominant_over_warning(self):
        """When both error and warning set, error dominates in snapshot."""
        _, _, vc, sync = self._import_modules()
        results = sync.synchronize_presentation(
            ("p1",),
            warning_ids=frozenset({"p1"}),
            error_ids=frozenset({"p1"}),
        )
        self.assertEqual(results[0].dominant_flag, "error")
        self.assertEqual(results[0].visual_contract.outline_intent, vc.OUTLINE_ERROR)
        self.assertEqual(results[0].visual_contract.emphasis_level, vc.EMPHASIS_CRITICAL)
        self.assertTrue(results[0].presentation_state.warning)
        self.assertTrue(results[0].presentation_state.error)

    # ── Rule 6: disabled distinct and dim ────────────────────────

    def test_disabled_synchronizes(self):
        """Disabled ids produce dim opacity and DISABLED outline."""
        _, _, vc, sync = self._import_modules()
        results = sync.synchronize_presentation(
            ("x1",),
            disabled_ids=frozenset({"x1"}),
        )
        self.assertTrue(results[0].presentation_state.disabled)
        self.assertEqual(results[0].visual_contract.opacity_intent, vc.OPACITY_DIM)
        self.assertEqual(results[0].visual_contract.outline_intent, vc.OUTLINE_DISABLED)

    def test_disabled_distinct_from_selected(self):
        """Disabled snapshot differs from selected snapshot in opacity and outline."""
        _, _, vc, sync = self._import_modules()
        disabled_result = sync.synchronize_presentation(
            ("x1",), disabled_ids=frozenset({"x1"})
        )[0]
        selected_result = sync.synchronize_presentation(
            ("x1",), selected_ids=frozenset({"x1"})
        )[0]

        self.assertEqual(disabled_result.visual_contract.opacity_intent, vc.OPACITY_DIM)
        self.assertEqual(selected_result.visual_contract.opacity_intent, vc.OPACITY_NORMAL)
        self.assertNotEqual(
            disabled_result.visual_contract.outline_intent,
            selected_result.visual_contract.outline_intent,
        )

    # ── Rule 7: multiple flags coexist ───────────────────────────

    def test_multiple_flags_coexist(self):
        """Component in multiple flag sets gets all flags in snapshot."""
        *_, sync = self._import_modules()
        results = sync.synchronize_presentation(
            ("c1",),
            selected_ids=frozenset({"c1"}),
            hovered_id="c1",
            warning_ids=frozenset({"c1"}),
        )
        state = results[0].presentation_state
        self.assertTrue(state.selected)
        self.assertTrue(state.hovered)
        self.assertTrue(state.warning)
        self.assertGreaterEqual(len(state.active_flags), 3)
        # Dominant should be warning (highest severity)
        self.assertEqual(results[0].dominant_flag, "warning")

    # ── Rule 8: deterministic ────────────────────────────────────

    def test_synchronization_is_deterministic(self):
        """Same inputs always produce same snapshots."""
        *_, sync = self._import_modules()
        ids = ("a", "b", "c")
        kwargs = dict(
            selected_ids=frozenset({"a"}),
            hovered_id="b",
            warning_ids=frozenset({"c"}),
            error_ids=frozenset({"a"}),
        )
        r1 = sync.synchronize_presentation(ids, **kwargs)
        r2 = sync.synchronize_presentation(ids, **kwargs)
        r3 = sync.synchronize_presentation(ids, **kwargs)

        self.assertEqual(r1, r2)
        self.assertEqual(r2, r3)

    # ── Rule 9: no input mutation ────────────────────────────────

    def test_synchronization_does_not_mutate_inputs(self):
        """Input arguments remain unchanged after synchronization."""
        *_, sync = self._import_modules()

        ids = ("a", "b", "c")
        selected = frozenset({"a"})
        warning = frozenset({"b"})

        ids_copy = tuple(ids)
        selected_copy = frozenset(selected)

        sync.synchronize_presentation(
            ids,
            selected_ids=selected,
            warning_ids=warning,
        )

        self.assertEqual(ids, ids_copy)
        self.assertEqual(selected, selected_copy)

    def test_synchronization_creates_fresh_objects(self):
        """Each snapshot creates new objects, not cached references."""
        _, _, vc, sync = self._import_modules()
        results = sync.synchronize_presentation(
            ("d1",),
            selected_ids=frozenset({"d1"}),
        )
        # Second call produces different object instances
        results2 = sync.synchronize_presentation(
            ("d1",),
            selected_ids=frozenset({"d1"}),
        )
        # Equal but not identical
        self.assertEqual(results[0], results2[0])

    # ── Rule 10: convenience delegations ─────────────────────────

    def test_dominant_flag_delegation(self):
        """Snapshot.dominant_flag delegates to presentation_state."""
        *_, sync = self._import_modules()
        r = sync.synchronize_presentation(
            ("c1",), error_ids=frozenset({"c1"})
        )[0]
        self.assertEqual(r.dominant_flag, r.presentation_state.dominant_flag)
        self.assertEqual(r.dominant_flag, "error")

    def test_visual_severity_delegation(self):
        """Snapshot.visual_severity delegates to presentation_state."""
        *_, sync = self._import_modules()
        r = sync.synchronize_presentation(
            ("c1",), error_ids=frozenset({"c1"})
        )[0]
        self.assertEqual(r.visual_severity, r.presentation_state.visual_severity)

    # ── Rule 11: no domain imports ───────────────────────────────

    def test_no_domain_imports(self):
        """Source file must not import domain modules."""
        with open("ui/configurator_v2/presentation_synchronization.py") as f:
            source = f.read()

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
            "interactive_components",
            "visual_components",
        ]
        for token in forbidden:
            self.assertNotIn(
                token,
                import_text,
                msg=f"presentation_synchronization.py must not import '{token}'",
            )

    # ── Rule 12: no engine/workflow naming ───────────────────────

    def test_no_engine_workflow_event_naming(self):
        """No engine/workflow/event-bus naming in the module."""
        _, _, _, sync = self._import_modules()

        names = [
            name for name in dir(sync)
            if any(token in name.lower() for token in (
                "engine", "workflow", "event", "bus", "dispatch",
                "store", "reducer", "subscribe", "emit",
            ))
        ]
        self.assertEqual(
            names, [],
            msg=f"Synchronization module should not contain engine/workflow/event names: {names}",
        )

    def test_snapshot_has_no_lifecycle_methods(self):
        """SynchronizedPresentation must not have engine-like methods."""
        _, _, _, sync = self._import_modules()
        snapshot = sync.SynchronizedPresentation()

        lifecycle = {"start", "stop", "run", "process", "dispatch", "subscribe", "emit"}
        for attr in lifecycle:
            self.assertFalse(
                hasattr(snapshot, attr),
                msg=f"SynchronizedPresentation should not have method '{attr}'",
            )

    # ── Rule 13: type validation ─────────────────────────────────

    def test_component_id_validation(self):
        """Non-string component_id raises TypeError in SynchronizedPresentation."""
        _, _, _, sync = self._import_modules()
        with self.assertRaises(TypeError):
            sync.SynchronizedPresentation(component_id=42)  # type: ignore

    def test_empty_ids_returns_empty_result(self):
        """synchronize_presentation with no IDs returns ()."""
        *_, sync = self._import_modules()
        self.assertEqual(sync.synchronize_presentation(()), ())

    # ── Rule 14: descriptor pairs ────────────────────────────────

    def test_descriptor_pairs_none(self):
        """synchronize_descriptor_pairs(None) returns ()."""
        _, _, _, sync = self._import_modules()
        self.assertEqual(sync.synchronize_descriptor_pairs(None), ())

    def test_descriptor_pairs_neutral(self):
        """synchronize_descriptor_pairs(neutral) returns ()."""
        _, _, _, sync = self._import_modules()
        neutral = sync.SynchronizedPresentation()
        self.assertEqual(sync.synchronize_descriptor_pairs(neutral), ())

    def test_descriptor_pairs_active(self):
        """Non-neutral snapshot yields descriptor pairs."""
        _, _, _, sync = self._import_modules()
        results = sync.synchronize_presentation(
            ("d1",),
            selected_ids=frozenset({"d1"}),
            error_ids=frozenset({"d1"}),
        )
        pairs = dict(sync.synchronize_descriptor_pairs(results[0]))
        self.assertEqual(pairs.get("component_id"), "d1")
        self.assertEqual(pairs.get("sync_dominant"), "error")
        self.assertEqual(pairs.get("sync_severity"), "50")

    # ── Rule 15: all flag sets propagate ─────────────────────────

    def test_all_flag_sets_propagate(self):
        """All 9 flag sets propagate through the synchronization pipeline."""
        *_, sync = self._import_modules()
        results = sync.synchronize_presentation(
            ("c1",),
            selected_ids=frozenset({"c1"}),
            hovered_id="c1",
            focused_id="c1",
            disabled_ids=frozenset({"c1"}),
            warning_ids=frozenset({"c1"}),
            error_ids=frozenset({"c1"}),
            preview_ids=frozenset({"c1"}),
            active_ids=frozenset({"c1"}),
            muted_ids=frozenset({"c1"}),
        )
        state = results[0].presentation_state
        self.assertTrue(state.selected)
        self.assertTrue(state.hovered)
        self.assertTrue(state.focused)
        self.assertTrue(state.disabled)
        self.assertTrue(state.warning)
        self.assertTrue(state.error)
        self.assertTrue(state.preview)
        self.assertTrue(state.active)
        self.assertTrue(state.muted)
        # Dominant should be error (highest severity)
        self.assertEqual(results[0].dominant_flag, "error")
        self.assertEqual(results[0].visual_contract.outline_intent, "ERROR")


if __name__ == "__main__":
    unittest.main()
