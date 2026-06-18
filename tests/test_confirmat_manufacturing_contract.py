import unittest

from domain.builders import WardrobeBuilder
from domain.core_types import NodeCategory
from domain.manufacturing_compiler import ManufacturingCompiler
from domain.rules_engine import RuleContext, System32JoineryRule


class TestConfirmatManufacturingContract(unittest.TestCase):

    def test_confirmat_placements_compile_to_physical_panel_machining_operations(self):
        project = self._project_with_divider_confirmat_joinery()
        context = RuleContext()

        placements = [
            placement
            for placement in System32JoineryRule().apply(project, context)
            if placement.hardware_intent == "INTENT_CONFIRMAT_50"
        ]
        project.placements.extend(placements)
        ManufacturingCompiler().compile(project, context)

        confirmat_ops = [
            op
            for node in project.graph.physical_nodes
            for op in getattr(node, "machining_ops", [])
            if self._is_confirmat_operation(op)
        ]
        virtual_confirmat_ops = [
            op
            for node in project.graph._by_category[NodeCategory.VIRTUAL]
            for op in getattr(node, "machining_ops", [])
            if self._is_confirmat_operation(op)
        ]

        host_ops = [
            op
            for node in project.graph.physical_nodes
            for op in getattr(node, "machining_ops", [])
            if op.op_type == "DRILL"
            and abs(op.diameter - 7.0) < 0.1
            and abs(op.depth - 18.0) < 0.1
        ]
        target_ops = [
            op
            for node in project.graph.physical_nodes
            for op in getattr(node, "machining_ops", [])
            if op.op_type == "DRILL"
            and abs(op.diameter - 5.0) < 0.1
            and abs(op.depth - 34.0) < 0.1
            and getattr(op, "axis", "Z") == "X"
        ]

        self.assertEqual(len(placements), 6)
        self.assertTrue(confirmat_ops)
        self.assertTrue(host_ops)
        self.assertTrue(target_ops)
        self.assertFalse(
            virtual_confirmat_ops and not confirmat_ops,
            "Confirmat drilling operations must not be attached only to virtual nodes",
        )
        self.assertTrue(
            all(
                project.graph.get_node(placement.host_node_id).category
                == NodeCategory.PHYSICAL
                for placement in placements
            )
        )
        self.assertTrue(
            all(
                project.graph.get_node(placement.target_node_id).category
                == NodeCategory.PHYSICAL
                for placement in placements
            )
        )

    @staticmethod
    def _project_with_divider_confirmat_joinery():
        cabinet = WardrobeBuilder(
            uid="CONFIRMAT_MANUFACTURING_CONTRACT",
            width=1000.0,
            height=2000.0,
            depth=600.0,
        )
        cabinet.add_divider(x_offset=400.0)
        return cabinet.build()

    @staticmethod
    def _is_confirmat_operation(op):
        if getattr(op, "op_type", "") != "DRILL":
            return False

        is_host_hole = (
            abs(op.diameter - 7.0) < 0.1
            and abs(op.depth - 18.0) < 0.1
        )
        is_target_hole = (
            abs(op.diameter - 5.0) < 0.1
            and abs(op.depth - 34.0) < 0.1
            and getattr(op, "axis", "Z") == "X"
        )
        return is_host_hole or is_target_hole


if __name__ == "__main__":
    unittest.main()
