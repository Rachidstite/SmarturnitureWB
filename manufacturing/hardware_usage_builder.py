from manufacturing.hardware_usage_report import HardwareUsageReport


class HardwareUsageBuilder:

    REQUIRED_KEYS = ("hardware_family", "hardware_sku", "hardware_intent")

    def build(self, manufacturing_package):
        report = HardwareUsageReport()
        sku_counts = {}
        family_counts = {}
        intent_counts = {}

        for operation in getattr(manufacturing_package, "machining_operations", []) or []:
            metadata = getattr(operation, "metadata", None) or {}
            if not self._has_complete_identity(metadata):
                continue

            family = str(metadata.get("hardware_family", "") or "").strip()
            sku = str(metadata.get("hardware_sku", "") or "").strip()
            intent = str(metadata.get("hardware_intent", "") or "").strip()

            if not family or not sku or not intent:
                continue

            sku_counts[sku] = sku_counts.get(sku, 0) + 1

            family_bucket = family_counts.setdefault(family, {})
            family_bucket[sku] = family_bucket.get(sku, 0) + 1

            intent_bucket = intent_counts.setdefault(intent, {})
            intent_bucket[sku] = intent_bucket.get(sku, 0) + 1

        report.hardware_sku_counts = sku_counts
        report.hardware_family_counts = family_counts
        report.hardware_intent_counts = intent_counts
        return report

    @staticmethod
    def _has_complete_identity(metadata):
        return all(
            str(metadata.get(key, "") or "").strip()
            for key in HardwareUsageBuilder.REQUIRED_KEYS
        )
