import unittest

class TestManufacturingPackageBuilder(unittest.TestCase):

    def test_builder_exists(self):
        from manufacturing.manufacturing_package_builder import (
            ManufacturingPackageBuilder
        )

        self.assertTrue(
            callable(
                ManufacturingPackageBuilder().build
            )
        )

if __name__ == "__main__":
    unittest.main()
