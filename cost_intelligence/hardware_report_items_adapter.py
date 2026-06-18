class HardwareReportItemsAdapter:

    HARDWARE_SKU_MAP = (
        ("MINIFIX", "MINIFIX_15_V1"),
        ("HINGE", "HINGE_BLUM_110_V1"),
        ("CONFIRMAT", "CONFIRMAT_50_V1"),
        ("SHELF_PIN", "SHELF_PIN_5MM"),
        ("DRAWER_SLIDE", "DRAWER_SLIDE_SOFTCLOSE_450"),
        ("HANDLE", "HANDLE_128_BLACK"),
    )

    DIRECT_SKUS = (
        "DRAWER_SLIDE_SOFTCLOSE_450",
        "DRAWER_SLIDE_STANDARD_450",
    )

    @staticmethod
    def from_report(report):
        hardware_items = getattr(report, "hardware_items", None) or {}
        items = []

        for hardware_key, sku in HardwareReportItemsAdapter.HARDWARE_SKU_MAP:
            if hardware_key == "DRAWER_SLIDE":
                direct_items = HardwareReportItemsAdapter._direct_drawer_slide_items(
                    hardware_items
                )
                if direct_items:
                    items.extend(direct_items)
                    continue

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

    @staticmethod
    def _direct_drawer_slide_items(hardware_items):
        items = []
        for sku in HardwareReportItemsAdapter.DIRECT_SKUS:
            quantity = hardware_items.get(sku)
            if quantity is None or quantity <= 0:
                continue

            items.append(
                {
                    "sku": sku,
                    "quantity": quantity,
                }
            )
        return items
