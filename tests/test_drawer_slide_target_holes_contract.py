import unittest

from domain.anchors import MountFace
from domain.hardware_library import HardwareRegistry


class TestDrawerSlideTargetHolesContract(unittest.TestCase):

    DRAWER_SLIDE_SKUS = (
        "DRAWER_SLIDE_SOFTCLOSE_450",
        "DRAWER_SLIDE_STANDARD_450",
    )

    def test_drawer_slides_have_drawer_side_target_screw_holes(self):
        registry = HardwareRegistry()

        for sku in self.DRAWER_SLIDE_SKUS:
            with self.subTest(sku=sku):
                hardware = registry.get_hardware(sku)

                self.assertIsNotNone(hardware)
                self.assertTrue(hardware.host_holes)
                self.assertTrue(
                    hardware.target_holes,
                    f"{sku} is missing drawer-side slide member target_holes",
                )

                screw_holes = [
                    hole
                    for hole in hardware.target_holes
                    if hole.diameter == 3.0
                    and hole.depth == 12.0
                    and hole.face == MountFace.LEFT
                    and not hole.is_through_hole
                ]

                self.assertTrue(
                    screw_holes,
                    f"{sku} target_holes must include 3.0mm x 12.0mm drawer-side screw holes",
                )


if __name__ == "__main__":
    unittest.main()
