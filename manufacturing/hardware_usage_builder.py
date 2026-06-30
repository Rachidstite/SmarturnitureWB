from manufacturing.hardware_usage_report import HardwareUsageReport


class HardwareUsageBuilder:

    REQUIRED_KEYS = ("hardware_family", "hardware_sku", "hardware_intent")

    def build(self, manufacturing_package):
        report = HardwareUsageReport()
        sku_counts = {}
        family_counts = {}
        intent_counts = {}
        sku_metadata = {}

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
            self._add_sku_metadata(sku_metadata, sku, family, metadata)

        report.hardware_sku_counts = sku_counts
        report.hardware_family_counts = family_counts
        report.hardware_intent_counts = intent_counts
        report.hardware_sku_metadata = self._freeze_sku_metadata(sku_metadata)
        return report

    @staticmethod
    def _has_complete_identity(metadata):
        return all(
            str(metadata.get(key, "") or "").strip()
            for key in HardwareUsageBuilder.REQUIRED_KEYS
        )

    @staticmethod
    def _add_sku_metadata(sku_metadata, sku, family, metadata):
        item = sku_metadata.setdefault(
            sku,
            {
                "description": "",
                "unit": "",
                "hardware_category": "",
                "component_reference": set(),
                "cabinet_reference": set(),
                "source_operation_references": set(),
            },
        )
        item["description"] = item["description"] or HardwareUsageBuilder._first_text(
            metadata,
            "hardware_description",
            "description",
        )
        item["unit"] = item["unit"] or HardwareUsageBuilder._first_text(
            metadata,
            "hardware_unit",
            "unit",
        )
        item["hardware_category"] = (
            item["hardware_category"]
            or HardwareUsageBuilder._first_text(
                metadata,
                "hardware_category",
                "category",
            )
            or family
        )
        HardwareUsageBuilder._add_reference(
            item["component_reference"],
            metadata,
            "component_reference",
            "component_id",
            "target_node_id",
            "host_node_id",
        )
        HardwareUsageBuilder._add_reference(
            item["cabinet_reference"],
            metadata,
            "cabinet_reference",
            "cabinet_id",
        )
        HardwareUsageBuilder._add_reference(
            item["source_operation_references"],
            metadata,
            "source_operation_reference",
            "source_operation_references",
            "source_operation_id",
            "source_operation_ids",
        )

    @staticmethod
    def _first_text(metadata, *keys):
        for key in keys:
            value = str(metadata.get(key, "") or "").strip()
            if value:
                return value
        return ""

    @staticmethod
    def _add_reference(bucket, metadata, *keys):
        for key in keys:
            value = str(metadata.get(key, "") or "").strip()
            if value:
                bucket.add(value)

    @staticmethod
    def _freeze_sku_metadata(sku_metadata):
        return {
            sku: {
                "description": values["description"],
                "unit": values["unit"],
                "hardware_category": values["hardware_category"],
                "component_reference": tuple(sorted(values["component_reference"])),
                "cabinet_reference": tuple(sorted(values["cabinet_reference"])),
                "source_operation_references": tuple(
                    sorted(values["source_operation_references"])
                ),
            }
            for sku, values in sku_metadata.items()
        }
