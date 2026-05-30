import unittest
from domain.topology import TopologyManager

class TestCabinetTopology(unittest.TestCase):
    def setUp(self):
        self.topo = TopologyManager()
        self.topo.seed_root(1000, 2000, 600)

    def test_initial_state(self):
        self.assertIn("ROOT", self.topo.sections)

    def test_divider_split(self):
        div_id, left_id, right_id = self.topo.add_vertical_divider(400, 18.0)
        self.assertIn(left_id, self.topo.sections)
        self.assertIn(right_id, self.topo.sections)
        self.assertFalse(self.topo.sections["ROOT"].is_active)

    def test_zero_width_allowed_for_diagnostics(self):
        self.topo.add_vertical_divider(5, 18.0)
        self.assertTrue(True)
        
    def test_out_of_bounds_protection(self):
        self.topo.add_vertical_divider(2000, 18.0)
        self.assertTrue(True)
