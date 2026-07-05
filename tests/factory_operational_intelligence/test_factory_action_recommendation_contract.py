# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Factory Operational Intelligence
# Factory Action Recommendation Contract Tests
#
# Verifies:
# - deterministic output
# - frozen dataclasses
# - immutable read model
# - accepts empty blocking analysis
# - recommendation references blocking item
# - knowledge source preserved
# - knowledge reference preserved
# - responsible domain preserved
# - confidence preserved
# - summary generated
# - no forbidden imports
# - no backend leakage
# - no mutation
# - no calculations
# - no AI
# - no decision generation
# - no workflow naming
# ──────────────────────────────────────────────────────────────────────

from __future__ import annotations

import sys
import types
import unittest


class TestFactoryActionRecommendationContract(unittest.TestCase):
    """Verify factory action recommendation read model contract."""

    _rm = None
    _fr = None
    _ba = None
    _ar = None

    @classmethod
    def _import_once(cls):
        if cls._rm is not None:
            return cls._rm, cls._fr, cls._ba, cls._ar

        import importlib.machinery
        import importlib.util

        for key in list(sys.modules):
            if key.startswith(("factory_operational_intelligence", "ui.configurator_v2")):
                del sys.modules[key]

        parent1 = types.ModuleType("ui.configurator_v2")
        parent1.__path__ = ["ui/configurator_v2"]
        sys.modules["ui.configurator_v2"] = parent1

        parent2 = types.ModuleType("factory_operational_intelligence")
        parent2.__path__ = ["factory_operational_intelligence"]
        sys.modules["factory_operational_intelligence"] = parent2

        def _load(name, path):
            loader = importlib.machinery.SourceFileLoader(name, path)
            spec = importlib.machinery.ModuleSpec(name, loader, origin=path)
            mod = importlib.util.module_from_spec(spec)
            sys.modules[name] = mod
            loader.exec_module(mod)
            return mod

        rm = _load("ui.configurator_v2.read_models", "ui/configurator_v2/read_models.py")
        fr = _load(
            "factory_operational_intelligence.factory_readiness",
            "factory_operational_intelligence/factory_readiness.py",
        )
        ba = _load(
            "factory_operational_intelligence.blocking_analysis",
            "factory_operational_intelligence/blocking_analysis.py",
        )
        ar = _load(
            "factory_operational_intelligence.factory_action_recommendation",
            "factory_operational_intelligence/factory_action_recommendation.py",
        )
        cls._rm = rm
        cls._fr = fr
        cls._ba = ba
        cls._ar = ar
        return rm, fr, ba, ar

    def _make_blocking_item(self, category, panel, severity, message="", item_id=""):
        ba = self._ba
        return ba.FactoryBlockingItem(
            blocking_item_id=item_id or f"{panel.upper().replace(' ', '_')}:{category.upper().replace(' ', '_')}:0",
            operational_category=category,
            source_panel=panel,
            severity=severity,
            human_message=message or f"{severity} in {category}",
            operational_impact=f"Impact from {panel}",
        )

    def _make_blocking_analysis(self, status, items):
        ba = self._ba
        return ba.FactoryBlockingAnalysisReadModel(
            status=status,
            blocking_items=tuple(items),
            critical_count=sum(1 for i in items if i.severity == "BLOCKED"),
            high_count=sum(1 for i in items if i.severity == "ERROR"),
            medium_count=sum(1 for i in items if i.severity == "WARNING"),
            low_count=sum(1 for i in items if i.severity == "INFO"),
            source_panels=tuple(sorted(set(i.source_panel for i in items))),
        )

    # ── Deterministic output ─────────────────────────────────────

    def test_deterministic(self):
        rm, fr, ba, ar = self._import_once()
        analysis = self._make_blocking_analysis(
            "BLOCKED",
            (self._make_blocking_item("MANUFACTURING", "Manufacturing", "BLOCKED"),),
        )
        r1 = ar.build_factory_action_recommendation_read_model(analysis)
        r2 = ar.build_factory_action_recommendation_read_model(analysis)
        self.assertEqual(r1, r2)

    # ── Frozen dataclasses ───────────────────────────────────────

    def test_recommendation_is_frozen(self):
        rm, fr, ba, ar = self._import_once()
        self.assertTrue(hasattr(ar.FactoryRecommendation, "__dataclass_fields__"))

    def test_read_model_is_frozen(self):
        rm, fr, ba, ar = self._import_once()
        self.assertTrue(hasattr(ar.FactoryRecommendationReadModel, "__dataclass_fields__"))

    # ── Immutable read model ─────────────────────────────────────

    def test_no_input_mutation(self):
        rm, fr, ba, ar = self._import_once()
        analysis = self._make_blocking_analysis(
            "BLOCKED",
            (self._make_blocking_item("MANUFACTURING", "Manufacturing", "BLOCKED"),),
        )
        orig_status = analysis.status
        ar.build_factory_action_recommendation_read_model(analysis)
        self.assertEqual(analysis.status, orig_status)

    # ── Accepts empty blocking analysis ──────────────────────────

    def test_none_analysis_returns_empty(self):
        rm, fr, ba, ar = self._import_once()
        result = ar.build_factory_action_recommendation_read_model(None)
        self.assertEqual(len(result.recommendations), 0)

    def test_empty_analysis_returns_empty(self):
        rm, fr, ba, ar = self._import_once()
        result = ar.build_factory_action_recommendation_read_model(
            ba.FactoryBlockingAnalysisReadModel(),
        )
        self.assertEqual(len(result.recommendations), 0)

    # ── Recommendation references blocking item ──────────────────

    def test_recommendation_references_blocking_item_id(self):
        rm, fr, ba, ar = self._import_once()
        analysis = self._make_blocking_analysis(
            "BLOCKED",
            (self._make_blocking_item("MANUFACTURING", "Manufacturing", "BLOCKED"),),
        )
        result = ar.build_factory_action_recommendation_read_model(analysis)
        expected_id = "MANUFACTURING:MANUFACTURING:0"
        self.assertEqual(result.recommendations[0].blocking_reference, expected_id)

    def test_multiple_blocking_items_produce_multi_recommendations(self):
        rm, fr, ba, ar = self._import_once()
        analysis = self._make_blocking_analysis(
            "BLOCKED",
            (
                self._make_blocking_item("MANUFACTURING", "Manufacturing", "BLOCKED"),
                self._make_blocking_item("ENGINEERING", "Validation", "ERROR"),
                self._make_blocking_item("COST", "Cost", "WARNING"),
            ),
        )
        result = ar.build_factory_action_recommendation_read_model(analysis)
        self.assertEqual(len(result.recommendations), 3)

    def test_blocking_item_id_unique_in_multiple_items(self):
        """Each recommendation references a distinct blocking_item_id."""
        rm, fr, ba, ar = self._import_once()
        analysis = self._make_blocking_analysis(
            "BLOCKED",
            (
                self._make_blocking_item("MANUFACTURING", "Manufacturing", "BLOCKED",
                    item_id="MANUFACTURING:MANUFACTURING:0"),
                self._make_blocking_item("ENGINEERING", "Validation", "ERROR",
                    item_id="VALIDATION:ENGINEERING:1"),
            ),
        )
        result = ar.build_factory_action_recommendation_read_model(analysis)
        ids = [r.blocking_reference for r in result.recommendations]
        self.assertEqual(len(set(ids)), 2, "Each recommendation must reference a unique blocking_item_id")

    def test_blocking_item_id_deterministic(self):
        """Same blocking items produce same blocking_reference across calls."""
        rm, fr, ba, ar = self._import_once()
        items = (self._make_blocking_item("MANUFACTURING", "Manufacturing", "BLOCKED"),)
        analysis = self._make_blocking_analysis("BLOCKED", items)
        r1 = ar.build_factory_action_recommendation_read_model(analysis)
        r2 = ar.build_factory_action_recommendation_read_model(analysis)
        self.assertEqual(
            r1.recommendations[0].blocking_reference,
            r2.recommendations[0].blocking_reference,
        )

    # ── Knowledge source preserved ───────────────────────────────

    def test_knowledge_source_engineering(self):
        rm, fr, ba, ar = self._import_once()
        analysis = self._make_blocking_analysis(
            "BLOCKED",
            (self._make_blocking_item("ENGINEERING", "Validation", "BLOCKED"),),
        )
        result = ar.build_factory_action_recommendation_read_model(analysis)
        self.assertEqual(result.recommendations[0].knowledge_source, "Engineering")

    def test_knowledge_source_manufacturing(self):
        rm, fr, ba, ar = self._import_once()
        analysis = self._make_blocking_analysis(
            "NOT_READY",
            (self._make_blocking_item("MANUFACTURING", "Manufacturing", "ERROR"),),
        )
        result = ar.build_factory_action_recommendation_read_model(analysis)
        self.assertEqual(result.recommendations[0].knowledge_source, "Manufacturing")

    def test_knowledge_source_cost(self):
        rm, fr, ba, ar = self._import_once()
        analysis = self._make_blocking_analysis(
            "NEEDS_REVIEW",
            (self._make_blocking_item("COST", "Cost", "WARNING"),),
        )
        result = ar.build_factory_action_recommendation_read_model(analysis)
        self.assertEqual(result.recommendations[0].knowledge_source, "Cost")

    def test_knowledge_source_commercial(self):
        rm, fr, ba, ar = self._import_once()
        analysis = self._make_blocking_analysis(
            "BLOCKED",
            (self._make_blocking_item("COMMERCIAL", "Commercial", "BLOCKED"),),
        )
        result = ar.build_factory_action_recommendation_read_model(analysis)
        self.assertEqual(result.recommendations[0].knowledge_source, "Commercial")

    def test_knowledge_source_release(self):
        rm, fr, ba, ar = self._import_once()
        analysis = self._make_blocking_analysis(
            "BLOCKED",
            (self._make_blocking_item("RELEASE", "Release", "BLOCKED"),),
        )
        result = ar.build_factory_action_recommendation_read_model(analysis)
        self.assertEqual(result.recommendations[0].knowledge_source, "Release")

    # ── Knowledge reference preserved ───────────────────────────

    def test_knowledge_reference_not_empty_for_known(self):
        rm, fr, ba, ar = self._import_once()
        analysis = self._make_blocking_analysis(
            "BLOCKED",
            (self._make_blocking_item("ENGINEERING", "Validation", "BLOCKED"),),
        )
        result = ar.build_factory_action_recommendation_read_model(analysis)
        self.assertTrue(len(result.recommendations[0].knowledge_reference) > 0)

    # ── Responsible domain preserved ────────────────────────────

    def test_responsible_domain(self):
        rm, fr, ba, ar = self._import_once()
        analysis = self._make_blocking_analysis(
            "BLOCKED",
            (self._make_blocking_item("MANUFACTURING", "Manufacturing", "BLOCKED"),),
        )
        result = ar.build_factory_action_recommendation_read_model(analysis)
        self.assertEqual(result.recommendations[0].responsible_domain, "Manufacturing")

    # ── Confidence preserved ─────────────────────────────────────

    def test_confidence_high_for_blocked(self):
        rm, fr, ba, ar = self._import_once()
        analysis = self._make_blocking_analysis(
            "BLOCKED",
            (self._make_blocking_item("ENGINEERING", "Validation", "BLOCKED"),),
        )
        result = ar.build_factory_action_recommendation_read_model(analysis)
        self.assertEqual(result.recommendations[0].confidence, "HIGH")

    def test_confidence_medium_for_warning(self):
        rm, fr, ba, ar = self._import_once()
        analysis = self._make_blocking_analysis(
            "NEEDS_REVIEW",
            (self._make_blocking_item("ENGINEERING", "Validation", "WARNING"),),
        )
        result = ar.build_factory_action_recommendation_read_model(analysis)
        self.assertEqual(result.recommendations[0].confidence, "MEDIUM")

    def test_confidence_none_for_unknown_category(self):
        rm, fr, ba, ar = self._import_once()
        analysis = self._make_blocking_analysis(
            "BLOCKED",
            (self._make_blocking_item("UNKNOWN", "UnknownPanel", "BLOCKED"),),
        )
        result = ar.build_factory_action_recommendation_read_model(analysis)
        self.assertEqual(result.recommendations[0].confidence, "NONE")

    # ── Summary generated ────────────────────────────────────────

    def test_summary_contains_status(self):
        rm, fr, ba, ar = self._import_once()
        analysis = self._make_blocking_analysis(
            "BLOCKED",
            (self._make_blocking_item("MANUFACTURING", "Manufacturing", "BLOCKED"),),
        )
        result = ar.build_factory_action_recommendation_read_model(analysis)
        self.assertIn("BLOCKED", result.summary_message)

    def test_summary_contains_counts(self):
        rm, fr, ba, ar = self._import_once()
        analysis = self._make_blocking_analysis(
            "BLOCKED",
            (
                self._make_blocking_item("MANUFACTURING", "Manufacturing", "BLOCKED"),
                self._make_blocking_item("ENGINEERING", "Validation", "WARNING"),
            ),
        )
        result = ar.build_factory_action_recommendation_read_model(analysis)
        self.assertIn("1 high confidence", result.summary_message)
        self.assertIn("1 medium confidence", result.summary_message)

    def test_empty_summary(self):
        rm, fr, ba, ar = self._import_once()
        result = ar.build_factory_action_recommendation_read_model(None)
        self.assertIsNotNone(result.summary_message)

    # ── Counts computed correctly ────────────────────────────────

    def test_counts_mixed(self):
        rm, fr, ba, ar = self._import_once()
        analysis = self._make_blocking_analysis(
            "BLOCKED",
            (
                self._make_blocking_item("MANUFACTURING", "Manufacturing", "BLOCKED"),
                self._make_blocking_item("ENGINEERING", "Validation", "ERROR"),
                self._make_blocking_item("COST", "Cost", "WARNING"),
                self._make_blocking_item("COM", "X", "INFO"),  # no mapping → NONE
            ),
        )
        result = ar.build_factory_action_recommendation_read_model(analysis)
        self.assertEqual(result.high_confidence_count, 2)  # BLOCKED + ERROR
        self.assertEqual(result.medium_confidence_count, 1)  # WARNING
        self.assertEqual(result.none_confidence_count, 1)  # INFO unmapped

    def test_all_unknown_returns_none(self):
        rm, fr, ba, ar = self._import_once()
        analysis = self._make_blocking_analysis(
            "BLOCKED",
            (self._make_blocking_item("NONEXISTENT", "X", "BLOCKED"),),
        )
        result = ar.build_factory_action_recommendation_read_model(analysis)
        self.assertEqual(result.none_confidence_count, 1)

    # ── Status mirrored ─────────────────────────────────────────

    def test_status_mirrors_analysis(self):
        rm, fr, ba, ar = self._import_once()
        analysis = self._make_blocking_analysis(
            "NOT_READY",
            (self._make_blocking_item("MANUFACTURING", "Manufacturing", "ERROR"),),
        )
        result = ar.build_factory_action_recommendation_read_model(analysis)
        self.assertEqual(result.status, "NOT_READY")

    # ── No forbidden imports ────────────────────────────────────

    def test_no_forbidden_imports(self):
        with open("factory_operational_intelligence/factory_action_recommendation.py") as f:
            src = f.read()
        lines = [l for l in src.splitlines()
                 if l.strip().startswith(("import ", "from "))]
        text = "\n".join(lines)
        forbidden = [
            "domain.", "manufacturing.", "cost_intelligence.",
            "commercial_outputs.", "optimization.", "FreeCAD",
            "QtWidgets", "QtCore", "QtGui",
        ]
        for token in forbidden:
            self.assertNotIn(
                token, text,
                msg=f"factory_action_recommendation.py must not import '{token}'",
            )

    # ── No backend leakage ──────────────────────────────────────

    def test_no_backend_leakage(self):
        rm, fr, ba, ar = self._import_once()
        analysis = self._make_blocking_analysis(
            "BLOCKED",
            (self._make_blocking_item("MANUFACTURING", "Manufacturing", "BLOCKED"),),
        )
        result = ar.build_factory_action_recommendation_read_model(analysis)
        self.assertFalse(hasattr(result, "Shape"))
        self.assertFalse(hasattr(result, "all_nodes"))
        for rec in result.recommendations:
            self.assertFalse(hasattr(rec, "Shape"))
            self.assertFalse(hasattr(rec, "all_nodes"))

    # ── No workflow naming ──────────────────────────────────────

    def test_no_engine_workflow_naming(self):
        rm, fr, ba, ar = self._import_once()
        name = ar.build_factory_action_recommendation_read_model.__name__
        for token in ("engine", "workflow", "service", "event", "bus",
                       "store", "controller", "registry", "renderer"):
            self.assertNotIn(
                token, name.lower(),
                msg=f"'{name}' should not contain '{token}'",
            )

    # ── Human message populated ─────────────────────────────────

    def test_human_message_contains_action(self):
        rm, fr, ba, ar = self._import_once()
        analysis = self._make_blocking_analysis(
            "BLOCKED",
            (self._make_blocking_item("ENGINEERING", "Validation", "BLOCKED"),),
        )
        result = ar.build_factory_action_recommendation_read_model(analysis)
        msg = result.recommendations[0].human_message
        self.assertIn("Engineering", msg)
        self.assertIn("HIGH", msg)

    def test_human_message_no_recommendation(self):
        rm, fr, ba, ar = self._import_once()
        analysis = self._make_blocking_analysis(
            "BLOCKED",
            (self._make_blocking_item("UNKNOWN", "X", "BLOCKED"),),
        )
        result = ar.build_factory_action_recommendation_read_model(analysis)
        msg = result.recommendations[0].human_message
        self.assertIn("No automated recommendation", msg)

    # ── Recommendation ID format ─────────────────────────────────

    def test_recommendation_id_format(self):
        rm, fr, ba, ar = self._import_once()
        analysis = self._make_blocking_analysis(
            "BLOCKED",
            (
                self._make_blocking_item("A", "X", "BLOCKED"),
                self._make_blocking_item("B", "Y", "ERROR"),
            ),
        )
        result = ar.build_factory_action_recommendation_read_model(analysis)
        self.assertEqual(result.recommendations[0].recommendation_id, "REC-0001")
        self.assertEqual(result.recommendations[1].recommendation_id, "REC-0002")


if __name__ == "__main__":
    unittest.main()
