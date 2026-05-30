import unittest
import os, json
from domain.builders import WardrobeBuilder

class TestGoldenMaster(unittest.TestCase):
    GOLDEN_FILE = os.path.join(os.path.dirname(__file__), 'golden_master_wardrobe.json')

    def _extract_geometric_snapshot(self, project) -> dict:
        snapshot = {
            "schema_version": 1, # Future-proofing
            "total_nodes": len(project.graph.physical_nodes),
            "total_joinery_edges": len(project.joinery.edges),
            "parts": []
        }
        
        for node in project.graph.physical_nodes:
            snapshot["parts"].append({
                "role": getattr(node, 'role', 'UNKNOWN'),
                "w": round(node.width, 2),
                "h": round(node.height, 2),
                "t": round(node.thickness, 2),
                "x": round(node.transform.x, 2),
                "z": round(node.transform.z, 2)
            })
            
        snapshot["parts"] = sorted(snapshot["parts"], key=lambda p: (p['role'], p['x'], p['z']))
        return snapshot

    def test_golden_master_math_drift(self):
        cabinet = WardrobeBuilder(uid="GOLDEN", width=2000, height=2200, depth=600)
        left_id, right_id = cabinet.add_divider(x_offset=800)
        cabinet.add_shelves(count=4, section_id=left_id)
        cabinet.add_doors(count=4)
        project = cabinet.build()
        
        current_snapshot = self._extract_geometric_snapshot(project)

        # إذا تغير الـ Schema، يتم حذف القديم لتوليد واحد جديد (Migration aware)
        if os.path.exists(self.GOLDEN_FILE):
            with open(self.GOLDEN_FILE, 'r', encoding='utf-8') as f:
                golden_snapshot = json.load(f)
            if golden_snapshot.get("schema_version", 0) < current_snapshot["schema_version"]:
                os.remove(self.GOLDEN_FILE)

        if not os.path.exists(self.GOLDEN_FILE):
            with open(self.GOLDEN_FILE, 'w', encoding='utf-8') as f:
                json.dump(current_snapshot, f, indent=4)
            self.skipTest("Golden Master file generated for Schema v1. Run again to validate.")
        else:
            with open(self.GOLDEN_FILE, 'r', encoding='utf-8') as f:
                golden_snapshot = json.load(f)
                
            self.assertEqual(current_snapshot["total_nodes"], golden_snapshot["total_nodes"], "Silent Drift: Node count changed!")
            self.assertEqual(current_snapshot["total_joinery_edges"], golden_snapshot["total_joinery_edges"], "Silent Drift: Joinery logic changed!")
            
            for curr_part, gold_part in zip(current_snapshot["parts"], golden_snapshot["parts"]):
                self.assertDictEqual(curr_part, gold_part, f"Silent Drift in {curr_part['role']}! Math has been altered.")
