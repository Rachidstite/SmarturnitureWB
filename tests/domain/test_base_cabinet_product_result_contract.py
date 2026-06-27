import inspect
import unittest
from dataclasses import asdict, fields, is_dataclass

import domain.base_cabinet_product_result as product_result_module
from domain.base_cabinet_product_result import BaseCabinetProductResult


class TestBaseCabinetProductResultContract(unittest.TestCase):
    def test_dataclass(self):
        self.assertTrue(is_dataclass(BaseCabinetProductResult))
        self.assertEqual(
            [field.name for field in fields(BaseCabinetProductResult)],
            [
                "specification",
                "scenario",
                "engineering",
                "validation",
                "manufacturing_outputs",
                "cost",
                "commercial",
                "quotation_document",
                "metadata",
                "diagnostics",
            ],
        )

    def test_frozen(self):
        result = BaseCabinetProductResult()

        with self.assertRaises((AttributeError, TypeError)):
            result.specification = object()

    def test_default_values(self):
        result = BaseCabinetProductResult()

        self.assertIsNone(result.specification)
        self.assertIsNone(result.scenario)
        self.assertIsNone(result.engineering)
        self.assertIsNone(result.validation)
        self.assertIsNone(result.manufacturing_outputs)
        self.assertIsNone(result.cost)
        self.assertIsNone(result.commercial)
        self.assertIsNone(result.quotation_document)
        self.assertEqual(result.metadata, {})
        self.assertEqual(result.diagnostics, ())

    def test_serialization_friendliness_with_asdict(self):
        result = BaseCabinetProductResult(
            specification={"kind": "spec"},
            scenario={"kind": "scenario"},
            engineering={"kind": "engineering"},
            validation={"kind": "validation"},
            manufacturing_outputs={"kind": "outputs"},
            cost={"kind": "cost"},
            commercial={"kind": "commercial"},
            quotation_document={"kind": "quotation_document"},
            metadata={"source": "base-cabinet"},
            diagnostics=("warning-1", "warning-2"),
        )

        data = asdict(result)

        self.assertEqual(data["specification"], {"kind": "spec"})
        self.assertEqual(data["scenario"], {"kind": "scenario"})
        self.assertEqual(data["engineering"], {"kind": "engineering"})
        self.assertEqual(data["validation"], {"kind": "validation"})
        self.assertEqual(data["manufacturing_outputs"], {"kind": "outputs"})
        self.assertEqual(data["cost"], {"kind": "cost"})
        self.assertEqual(data["commercial"], {"kind": "commercial"})
        self.assertEqual(
            data["quotation_document"], {"kind": "quotation_document"}
        )
        self.assertEqual(data["metadata"], {"source": "base-cabinet"})
        self.assertEqual(data["diagnostics"], ("warning-1", "warning-2"))

    def test_equality(self):
        first = BaseCabinetProductResult(
            specification="spec",
            scenario="scenario",
            engineering="engineering",
            validation="validation",
            manufacturing_outputs="outputs",
            cost="cost",
            commercial="commercial",
            quotation_document="quotation_document",
            metadata={"source": "base-cabinet"},
            diagnostics=("d1",),
        )
        second = BaseCabinetProductResult(
            specification="spec",
            scenario="scenario",
            engineering="engineering",
            validation="validation",
            manufacturing_outputs="outputs",
            cost="cost",
            commercial="commercial",
            quotation_document="quotation_document",
            metadata={"source": "base-cabinet"},
            diagnostics=("d1",),
        )

        self.assertEqual(first, second)

    def test_metadata_default_is_not_shared(self):
        first = BaseCabinetProductResult()
        second = BaseCabinetProductResult()

        first.metadata["source"] = "base-cabinet"

        self.assertEqual(second.metadata, {})
        self.assertIsNot(first.metadata, second.metadata)

    def test_diagnostics_default_is_immutable_tuple(self):
        result = BaseCabinetProductResult()

        self.assertIsInstance(result.diagnostics, tuple)
        self.assertEqual(result.diagnostics, ())
        self.assertFalse(hasattr(result.diagnostics, "append"))

    def test_no_runtime_behavior(self):
        result = BaseCabinetProductResult()

        self.assertFalse(hasattr(result, "build"))
        self.assertFalse(hasattr(result, "run"))
        self.assertFalse(hasattr(result, "execute"))

    def test_no_freecad_import_in_source(self):
        source = inspect.getsource(product_result_module)
        self.assertNotIn("FreeCAD", source)

    def test_no_manufacturing_runtime_import_in_source(self):
        source = inspect.getsource(product_result_module)
        self.assertNotIn("from manufacturing", source.lower())
        self.assertNotIn("import manufacturing", source.lower())


if __name__ == "__main__":
    unittest.main()
