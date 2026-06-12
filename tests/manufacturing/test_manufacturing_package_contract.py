import unittest
from dataclasses import is_dataclass

class TestManufacturingPackageContract(unittest.TestCase):

    def test_contract_exists(self):
        from manufacturing.manufacturing_package import ManufacturingPackage

        self.assertTrue(
            is_dataclass(ManufacturingPackage)
        )

if __name__ == "__main__":
    unittest.main()
