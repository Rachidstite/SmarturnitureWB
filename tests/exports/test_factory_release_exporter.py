import inspect
import unittest


class TestFactoryReleaseExporter(unittest.TestCase):
    """Exporter-layer tests for FactoryReleasePackage.

    The exporter is a read-only view/serializer.  All tests verify
    safe export behaviour on real and synthetic packages.
    """

    # -- helpers ------------------------------------------------------------

    @staticmethod
    def _make_decision(status="PASS", ready=True, warning_reasons=()):
        return type(
            "Decision",
            (),
            {
                "status": status,
                "ready_for_production": ready,
                "warning_reasons": warning_reasons,
            },
        )()

    @staticmethod
    def _make_object_with(field_name, items):
        return type("Obj", (), {field_name: items})()

    # -- 1.  Exporter accepts FactoryReleasePackage -------------------------

    def test_exporter_accepts_factory_release_package(self):
        from exports.factory_release_exporter import FactoryReleaseExporter
        from manufacturing.factory_release_package import FactoryReleasePackage

        result = FactoryReleaseExporter.export(FactoryReleasePackage())
        self.assertIsInstance(result, dict)

    # -- 2.  Export includes decision status --------------------------------

    def test_export_includes_decision_status(self):
        from exports.factory_release_exporter import FactoryReleaseExporter
        from manufacturing.factory_release_package import FactoryReleasePackage

        decision = self._make_decision(status="PASS", ready=True)
        package = FactoryReleasePackage(manufacturing_decision=decision)
        d = FactoryReleaseExporter.export(package)

        self.assertEqual(d["manufacturing_decision_status"], "PASS")
        self.assertTrue(d["ready_for_production"])

    # -- 3.  Export includes counts -----------------------------------------

    def test_export_includes_counts(self):
        from exports.factory_release_exporter import FactoryReleaseExporter
        from manufacturing.factory_release_package import FactoryReleasePackage

        cut_list = self._make_object_with("items", [{"id": 1}, {"id": 2}])
        hardware_bom = self._make_object_with("bom_rows", [{"sku": "H1"}])
        cnc_package = self._make_object_with("rows", [{"op": "drill"}])
        assembly_package = self._make_object_with("rows", [{"group": "A"}])

        package = FactoryReleasePackage(
            cut_list=cut_list,
            hardware_bom=hardware_bom,
            cnc_package=cnc_package,
            assembly_package=assembly_package,
        )
        d = FactoryReleaseExporter.export(package)

        self.assertEqual(d["cut_list_item_count"], 2)
        self.assertEqual(d["hardware_bom_row_count"], 1)
        self.assertEqual(d["cnc_row_count"], 1)
        self.assertEqual(d["assembly_row_count"], 1)

    # -- 4.  Export includes warnings ---------------------------------------

    def test_export_includes_warnings(self):
        from exports.factory_release_exporter import FactoryReleaseExporter
        from manufacturing.factory_release_package import FactoryReleasePackage

        decision = self._make_decision(
            status="WARNING", ready=False, warning_reasons=["Hinge evidence missing"]
        )
        package = FactoryReleasePackage(
            manufacturing_decision=decision,
            warnings=["release-warning-1", "release-warning-2"],
        )
        d = FactoryReleaseExporter.export(package)

        self.assertEqual(d["warning_reasons"], ["Hinge evidence missing"])
        self.assertEqual(
            d["release_warnings"], ["release-warning-1", "release-warning-2"]
        )

    # -- 5.  Empty package exports safely -----------------------------------

    def test_empty_package_exports_safely(self):
        from exports.factory_release_exporter import FactoryReleaseExporter
        from manufacturing.factory_release_package import FactoryReleasePackage

        d = FactoryReleaseExporter.export(FactoryReleasePackage())

        self.assertEqual(d["manufacturing_decision_status"], "")
        self.assertFalse(d["ready_for_production"])
        self.assertEqual(d["warning_reasons"], [])
        self.assertEqual(d["release_warnings"], [])
        self.assertEqual(d["cut_list_item_count"], 0)
        self.assertEqual(d["hardware_bom_row_count"], 0)
        self.assertEqual(d["cnc_row_count"], 0)
        self.assertEqual(d["assembly_row_count"], 0)
        self.assertEqual(d["metadata"], {})

    # -- 6.  No builder/validator/GeometryEngine/SceneGraph dependency ------

    def test_no_builder_validator_geometry_scenegraph_dependency(self):
        import exports.factory_release_exporter as module

        # Check the module's actual import chain — the only real
        # dependency vector.  Docstring mentions are harmless.
        import_expr = module.__name__
        # Inspect the file as text but only for import statements
        with open(module.__file__) as f:
            lines = f.readlines()

        import_lines = [l for l in lines if l.strip().startswith("import") or l.strip().startswith("from")]

        for line in import_lines:
            for token in (
                "ManufacturingDecisionBuilder",
                "HardwareBomBuilder",
                "ManufacturingCutlistBuilder",
                "ManufacturingProductionPackageBuilder",
                "CNCReportBuilder",
                "AssemblyPackageBuilder",
                "BaseApplicationService",
                "GeometryEngine",
                "SceneGraph",
                "Validator",
            ):
                self.assertNotIn(
                    token,
                    line,
                    msg=f"Exporter must not import '{token}' (found in: {line.strip()})",
                )

    # -- 7.  Export returns plain dict with expected keys -------------------

    def test_export_returns_plain_dict_with_expected_keys(self):
        from exports.factory_release_exporter import FactoryReleaseExporter
        from manufacturing.factory_release_package import FactoryReleasePackage

        d = FactoryReleaseExporter.export(FactoryReleasePackage())
        self.assertIsInstance(d, dict)
        self.assertEqual(
            set(d.keys()),
            {
                "manufacturing_decision_status",
                "ready_for_production",
                "warning_reasons",
                "release_warnings",
                "cut_list_item_count",
                "hardware_bom_row_count",
                "cnc_row_count",
                "assembly_row_count",
                "metadata",
            },
        )

    # -- 8.  render_text returns deterministic string -----------------------

    def test_render_text_deterministic(self):
        from exports.factory_release_exporter import FactoryReleaseExporter
        from manufacturing.factory_release_package import FactoryReleasePackage

        package = FactoryReleasePackage(
            warnings=["warn"],
            metadata={"v": "1"},
        )
        t1 = FactoryReleaseExporter.render_text(package)
        t2 = FactoryReleaseExporter.render_text(package)
        self.assertEqual(t1, t2)
        self.assertIn("Manufacturing Decision Status", t1)
        self.assertIn("warn", t1)
        self.assertIn("v", t1)

    # -- 9.  render_text includes key fields --------------------------------

    def test_render_text_includes_warnings_and_metadata(self):
        from exports.factory_release_exporter import FactoryReleaseExporter
        from manufacturing.factory_release_package import FactoryReleasePackage

        decision = self._make_decision(
            status="WARNING", ready=False, warning_reasons=["Hinge"]
        )
        package = FactoryReleasePackage(
            manufacturing_decision=decision,
            warnings=["Release warning"],
            metadata={"version": "1.0"},
        )
        text = FactoryReleaseExporter.render_text(package)
        self.assertIn("WARNING", text)
        self.assertIn("Release warning", text)
        self.assertIn("Hinge", text)
        self.assertIn("version", text)

    # -- 10.  Exporter does not modify the package --------------------------

    def test_exporter_does_not_modify_package(self):
        from exports.factory_release_exporter import FactoryReleaseExporter
        from manufacturing.factory_release_package import FactoryReleasePackage

        decision = self._make_decision(status="PASS", ready=True)
        warnings = ["w"]
        metadata = {"k": "v"}
        package = FactoryReleasePackage(
            manufacturing_decision=decision,
            warnings=warnings,
            metadata=metadata,
        )
        before_id = id(package)

        FactoryReleaseExporter.export(package)
        FactoryReleaseExporter.render_text(package)

        self.assertEqual(id(package), before_id)


if __name__ == "__main__":
    unittest.main()
