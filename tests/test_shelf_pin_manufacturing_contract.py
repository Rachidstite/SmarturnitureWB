import unittest

from domain.builders import WardrobeBuilder
from domain.core_types import NodeCategory, NodeRole
from domain.manufacturing_compiler import ManufacturingCompiler
from domain.rules_engine import RuleContext, ShelfSupportRule


class TestShelfPinManufacturingContract(unittest.TestCase):

    def test_shelf_support_generates_drilling_operations_on_physical_side_panels(self):
        cabinet = WardrobeBuilder(
            uid="SHELF_PIN_MANUFACTURING_CONTRACT",
            width=800.0,
            height=1800.0,
            depth=580.0,
        )
        cabinet.add_shelves(count=1, section_id="ROOT")
        project = cabinet.build()
        context = RuleContext()

        project.placements.extend(ShelfSupportRule().apply(project, context))
        ManufacturingCompiler().compile(project, context)

        side_panel_ops = [
            op
            for panel in project.graph._by_role[NodeRole.SIDE_PANEL]
            for op in getattr(panel, "machining_ops", [])
            if op.op_type == "DRILL"
            and abs(op.diameter - 5.0) < 0.1
            and abs(op.depth - 12.0) < 0.1
        ]
        virtual_anchor_ops = [
            op
            for node in project.graph._by_category[NodeCategory.VIRTUAL]
            for op in getattr(node, "machining_ops", [])
            if op.op_type == "DRILL"
            and abs(op.diameter - 5.0) < 0.1
            and abs(op.depth - 12.0) < 0.1
        ]

        self.assertTrue(
            project.placements,
            "ShelfSupportRule must emit shelf pin placements for shelves",
        )
        self.assertTrue(
            side_panel_ops,
            "Shelf pin drilling operations must be attached to physical side panels",
        )
        self.assertFalse(
            virtual_anchor_ops and not side_panel_ops,
            "Shelf pin drilling operations must not be attached only to virtual anchors",
        )


if __name__ == "__main__":
    unittest.main()
