from manufacturing.manufacturing_package import ManufacturingPackage


class ManufacturingPackageBuilder:

    def build(
        self,
        panels=None,
        materials=None,
        machining_operations=None,
        edge_operations=None,
        warnings=None,
    ):
        return ManufacturingPackage(
            panels=panels or [],
            materials=materials or [],
            machining_operations=machining_operations or [],
            edge_operations=edge_operations or [],
            warnings=warnings or [],
        )
