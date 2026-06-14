class HardwareReportItemsAdapter:

    HARDWARE_SKU_MAP = (
        ("MINIFIX", "MINIFIX_15_V1"),
        ("HINGE", "HINGE_BLUM_110_V1"),
    )

    @staticmethod
    def from_report(report):
        hardware_items = getattr(report, "hardware_items", None) or {}
        items = []

        for hardware_key, sku in HardwareReportItemsAdapter.HARDWARE_SKU_MAP:
            quantity = hardware_items.get(hardware_key)
            if quantity is None or quantity <= 0:
                continue

            items.append(
                {
                    "sku": sku,
                    "quantity": quantity,
                }
            )

        return items
