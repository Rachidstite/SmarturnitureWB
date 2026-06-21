from domain.hardware_library import HardwareRegistry
from manufacturing.hardware_intelligence_report import HardwareIntelligenceReport


class HardwareIntelligenceBuilder:
    FAMILY_BY_SKU = {
        "HINGE_BLUM_110_V1": "HINGE",
        "MINIFIX_15_V1": "MINIFIX",
        "CONFIRMAT_50_V1": "CONFIRMAT",
        "SHELF_PIN_5MM": "SHELF_PIN",
        "DRAWER_SLIDE_SOFTCLOSE_450": "DRAWER_SLIDE",
        "DRAWER_SLIDE_STANDARD_450": "DRAWER_SLIDE",
        "HANDLE_128_BLACK": "HANDLE",
    }

    def __init__(self, registry=None, family_by_sku=None):
        self.registry = registry or HardwareRegistry()
        self.family_by_sku = dict(family_by_sku or self.FAMILY_BY_SKU)

    def build(self, project, context):
        placements = list(getattr(project, "placements", []) or [])
        hardware_profile = dict(getattr(context, "hardware_profile", {}) or {})
        reports_by_family = {}

        for placement in placements:
            intent = str(getattr(placement, "hardware_intent", "") or "")
            if not intent:
                continue

            sku = hardware_profile.get(intent)
            if not sku:
                family = self._family_from_intent(intent)
                report = reports_by_family.setdefault(
                    family,
                    HardwareIntelligenceReport(hardware_family=family),
                )
                report.total_hardware_items += 1
                report.requires_review = True
                report.manufacturing_warning = (
                    f"Missing hardware profile mapping for {intent}"
                )
                report.recommended_action = (
                    "Map hardware intent to SKU in RuleContext.hardware_profile"
                )
                continue

            hardware_spec = self.registry.get_hardware(sku)
            family = (
                str(getattr(hardware_spec, "hardware_family", "") or "").strip()
                or self.family_by_sku.get(sku)
                or sku
            )
            report = reports_by_family.setdefault(
                family,
                HardwareIntelligenceReport(hardware_family=family),
            )
            report.total_hardware_items += 1

            if hardware_spec is None:
                report.requires_review = True
                report.manufacturing_warning = f"Missing hardware specification for {sku}"
                report.recommended_action = "Register hardware SKU in HardwareRegistry"
                continue

            report.total_host_holes += len(getattr(hardware_spec, "host_holes", []) or [])
            report.total_target_holes += len(
                getattr(hardware_spec, "target_holes", []) or []
            )
            report.total_face_holes += self._face_hole_count(hardware_spec)
            report.total_edge_holes += self._edge_hole_count(hardware_spec)

        return list(reports_by_family.values())

    @staticmethod
    def _family_from_intent(intent):
        return str(intent).replace("INTENT_", "", 1) or "UNKNOWN"

    @staticmethod
    def _edge_hole_count(hardware_spec):
        return sum(
            1
            for hole in HardwareIntelligenceBuilder._all_holes(hardware_spec)
            if str(getattr(hole, "axis", "Z")).upper() in {"X", "Y"}
        )

    @staticmethod
    def _face_hole_count(hardware_spec):
        return sum(
            1
            for hole in HardwareIntelligenceBuilder._all_holes(hardware_spec)
            if str(getattr(hole, "axis", "Z")).upper() not in {"X", "Y"}
        )

    @staticmethod
    def _all_holes(hardware_spec):
        return list(getattr(hardware_spec, "host_holes", []) or []) + list(
            getattr(hardware_spec, "target_holes", []) or []
        )
