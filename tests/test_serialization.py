import unittest
import os, tempfile
from domain.builders import WardrobeBuilder
from domain.serialization import ProjectSerializer
# إعادة استخدام مستخرج المعيار الذهبي للتأكد من التطابق التام
from tests.test_golden_master import TestGoldenMaster

class TestProjectSerialization(unittest.TestCase):
    def test_lossless_round_trip(self):
        """يبني خزانة، يحفظها في ملف، يعيد تحميلها، ويتأكد أن الهندسة متطابقة 100%"""
        # 1. Build Original
        cabinet = WardrobeBuilder(uid="SERIAL_TEST", width=1200, height=2000, depth=600)
        left_id, right_id = cabinet.add_divider(600)
        cabinet.add_shelves(count=3, section_id=left_id)
        cabinet.add_doors(count=2)
        original_project = cabinet.build()
        
        # 2. Save to Temp File
        with tempfile.TemporaryDirectory() as tmpdirname:
            filepath = os.path.join(tmpdirname, "project.json")
            ProjectSerializer.save(original_project, filepath)
            self.assertTrue(os.path.exists(filepath), "Project file was not created!")
            
            # 3. Load into New Instance
            loaded_project = ProjectSerializer.load(filepath)
        
        # 4. Extract Snapshots
        golden_extractor = TestGoldenMaster()
        original_snapshot = golden_extractor._extract_geometric_snapshot(original_project)
        loaded_snapshot = golden_extractor._extract_geometric_snapshot(loaded_project)
        
        # 5. Deep Validation
        self.assertEqual(original_snapshot["total_nodes"], loaded_snapshot["total_nodes"], "Node count mismatch after load!")
        self.assertEqual(original_snapshot["total_joinery_edges"], loaded_snapshot["total_joinery_edges"], "Joinery mismatch after load!")
        
        for orig_part, loaded_part in zip(original_snapshot["parts"], loaded_snapshot["parts"]):
            self.assertDictEqual(orig_part, loaded_part, f"Geometric corruption during serialization for {orig_part['role']}")
