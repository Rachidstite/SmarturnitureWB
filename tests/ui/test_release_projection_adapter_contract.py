# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Configurator V2
# Release Projection Adapter Contract Tests
#
# Verifies adapter contract for the final review domain.
# ──────────────────────────────────────────────────────────────────────

from __future__ import annotations

import sys
import types
import unittest


class _FakeRelItem:
    def __init__(self, label="", category="", status="", severity="",
                 message="", timestamp="", reviewer="", note="", component_id=""):
        self.item_label = label
        self.item_category = category
        self.item_status = status
        self.item_severity = severity
        self.item_message = message
        self.item_timestamp = timestamp
        self.reviewer = reviewer
        self.customer_note = note
        self.component_id = component_id


class _FakeRelSource:
    def __init__(self, items):
        self.release_items = list(items)


class TestReleaseProjectionAdapterContract(unittest.TestCase):

    @classmethod
    def _import_adapter(cls):
        import importlib.machinery, importlib.util
        for k in list(sys.modules):
            if k.startswith("ui.configurator_v2"): del sys.modules[k]
        parent = types.ModuleType("ui.configurator_v2")
        parent.__path__ = ["ui/configurator_v2"]
        sys.modules["ui.configurator_v2"] = parent
        def _load(n, p):
            l = importlib.machinery.SourceFileLoader(n, p)
            s = importlib.machinery.ModuleSpec(n, l, origin=p)
            m = importlib.util.module_from_spec(s)
            sys.modules[n] = m; l.exec_module(m); return m
        rm = _load("ui.configurator_v2.read_models", "ui/configurator_v2/read_models.py")
        pa = _load("ui.configurator_v2.projection_adapters", "ui/configurator_v2/projection_adapters.py")
        return rm, pa

    def test_converts_release_source(self):
        rm, pa = self._import_adapter()
        s = _FakeRelSource([
            _FakeRelItem("Design Approved", "Checklist", status="DONE"),
            _FakeRelItem("QA Signoff", "Approvals", status="PENDING"),
        ])
        r = pa.build_release_review_projection(s)
        self.assertIsInstance(r, rm.ReviewPanelReadModel)
        self.assertEqual(r.panel_name, "Release")
        self.assertTrue(r.available)

    def test_duck_typed_items(self):
        rm, pa = self._import_adapter()
        s = _FakeRelSource([
            _FakeRelItem("Check A", "Checklist", status="DONE"),
            _FakeRelItem("Approve B", "Approvals", status="PENDING"),
        ])
        r = pa.build_release_review_projection(s)
        sn = {sec.section_name for sec in r.sections}
        self.assertIn("Checklist", sn)
        self.assertIn("Approvals", sn)

    def test_dict_source(self):
        rm, pa = self._import_adapter()
        s = {"release_items": [
            {"item_label": "Step 1", "item_category": "Checklist", "item_status": "RELEASED"},
            {"item_label": "Need OK", "item_category": "Blocked", "item_severity": "BLOCKER"},
        ]}
        r = pa.build_release_review_projection(s)
        self.assertGreater(len(r.sections), 0)

    def test_list_source(self):
        rm, pa = self._import_adapter()
        r = pa.build_release_review_projection([
            _FakeRelItem("A", "Checklist"),
            _FakeRelItem("B", "Ready"),
        ])
        self.assertTrue(r.available)

    def test_tuple_source(self):
        rm, pa = self._import_adapter()
        r = pa.build_release_review_projection((
            _FakeRelItem("Done", "Released"),
        ))
        self.assertTrue(r.available)
        sn = {s.section_name for s in r.sections}
        self.assertIn("Ready", sn)

    def test_checklist_items_key(self):
        rm, pa = self._import_adapter()
        class S:
            def __init__(self): self.checklist_items = [_FakeRelItem("A", "Checklist")]
        r = pa.build_release_review_projection(S())
        self.assertTrue(r.available)

    def test_approvals_key(self):
        rm, pa = self._import_adapter()
        class S:
            def __init__(self): self.approvals = [_FakeRelItem("Sign", "Approvals")]
        r = pa.build_release_review_projection(S())
        self.assertTrue(r.available)
        sn = {s.section_name for s in r.sections}
        self.assertIn("Approvals", sn)

    def test_output_cv2_only(self):
        _, pa = self._import_adapter()
        s = _FakeRelSource([_FakeRelItem("A", "Checklist")])
        r = pa.build_release_review_projection(s)
        self.assertFalse(hasattr(r, "Shape"))
        for sec in r.sections:
            for row in sec.rows:
                self.assertIsInstance(row, tuple)
                self.assertEqual(len(row), 2)

    def test_no_backend_leak(self):
        _, pa = self._import_adapter()
        s = _FakeRelSource([_FakeRelItem("A", "Checklist")])
        r = pa.build_release_review_projection(s)
        for sec in r.sections:
            for row in sec.rows:
                self.assertNotIn("item_status", row[1].lower())
                self.assertNotIn("item_label", row[1].lower())

    def test_fields_preserved(self):
        _, pa = self._import_adapter()
        s = [_FakeRelItem("Sign Off", "Approvals", status="PENDING", severity="INFO",
                          message="Awaiting manager", timestamp="2026-07-05",
                          reviewer="Jane", note="Urgent", component_id="rel-1")]
        r = pa.build_release_review_projection(s)
        a = [s for s in r.sections if s.section_name == "Approvals"][0]
        v = a.rows[0][1]
        self.assertIn("PENDING", v)
        self.assertIn("INFO", v)
        self.assertIn("Awaiting manager", v)
        self.assertIn("2026-07-05", v)
        self.assertIn("[by: Jane]", v)
        self.assertIn("[note: Urgent]", v)
        self.assertIn("[rel-1]", v)

    def test_missing_label_safe(self):
        _, pa = self._import_adapter()
        r = pa.build_release_review_projection([{"item_category": "Checklist"}])
        c = [s for s in r.sections if s.section_name == "Checklist"]
        self.assertEqual(len(c), 1)

    def test_no_category_goes_to_other(self):
        _, pa = self._import_adapter()
        r = pa.build_release_review_projection([{"item_label": "Misc"}])
        o = [s for s in r.sections if s.section_name == "Other"]
        self.assertEqual(len(o), 1)

    def test_blocked_section(self):
        _, pa = self._import_adapter()
        s = [_FakeRelItem("Critical Issue", "Blocked", severity="BLOCKER", message="Cannot release")]
        r = pa.build_release_review_projection(s)
        b = [s for s in r.sections if s.section_name == "Blocked"]
        self.assertEqual(len(b), 1)
        self.assertGreater(len(b[0].warnings), 0)

    def test_none_source(self):
        rm, pa = self._import_adapter()
        r = pa.build_release_review_projection(None)
        self.assertFalse(r.available)
        self.assertEqual(len(r.sections), 0)

    def test_empty_items(self):
        _, pa = self._import_adapter()
        r = pa.build_release_review_projection([])
        self.assertFalse(r.available)
        self.assertEqual(len(r.sections), 1)
        self.assertEqual(r.sections[0].rows[0][0], "Status")

    def test_deterministic(self):
        _, pa = self._import_adapter()
        s = _FakeRelSource([_FakeRelItem("A", "Checklist", status="DONE")])
        self.assertEqual(
            pa.build_release_review_projection(s),
            pa.build_release_review_projection(s),
        )

    def test_no_mutation(self):
        _, pa = self._import_adapter()
        items = [_FakeRelItem("A", "Checklist")]
        s = _FakeRelSource(items)
        orig = items[0].item_label
        pa.build_release_review_projection(s)
        self.assertEqual(items[0].item_label, orig)

    def test_no_readiness_calculation(self):
        """No Ready section unless item with ready/done category exists."""
        _, pa = self._import_adapter()
        r = pa.build_release_review_projection([_FakeRelItem("A", "Checklist", status="DONE")])
        ready = [s for s in r.sections if s.section_name == "Ready"]
        self.assertEqual(len(ready), 0)

    def test_no_approval_inference(self):
        """No Approvals section unless item with approval category exists."""
        _, pa = self._import_adapter()
        r = pa.build_release_review_projection([_FakeRelItem("A", "Checklist")])
        appr = [s for s in r.sections if s.section_name == "Approvals"]
        self.assertEqual(len(appr), 0)

    def test_no_blocking_inference(self):
        """Blocked section only from explicit Blocked category, not from severity alone."""
        _, pa = self._import_adapter()
        r = pa.build_release_review_projection([_FakeRelItem("A", "Checklist", severity="BLOCKER")])
        blocked = [s for s in r.sections if s.section_name == "Blocked"]
        self.assertEqual(len(blocked), 0)  # severity triggers Warnings, not Blocked

    def test_no_forbidden_imports(self):
        with open("ui/configurator_v2/projection_adapters.py") as f:
            src = f.read()
        lines = [l for l in src.splitlines() if l.strip().startswith(("import ", "from "))]
        t = "\n".join(lines)
        for tok in ("domain.", "commercial_outputs.", "cost_intelligence.",
                     "manufacturing.", "optimization.", "FreeCAD",
                     "QtWidgets", "QtCore", "QtGui"):
            self.assertNotIn(tok, t, msg=f"must not import '{tok}'")

    def test_no_engine_workflow_naming(self):
        _, pa = self._import_adapter()
        n = pa.build_release_review_projection.__name__
        for tok in ("engine", "workflow", "service", "event", "bus",
                     "store", "controller", "registry", "renderer"):
            self.assertNotIn(tok, n.lower(), msg=f"'{n}' should not contain '{tok}'")


if __name__ == "__main__":
    unittest.main()
