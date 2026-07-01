from __future__ import annotations

from dataclasses import dataclass

from domain.product_configuration import ProductConfiguration


@dataclass(frozen=True)
class ProductConfigurationFamilyClassification:
    family_id: str
    executable_family: bool
    engineering_path: str | None
    reason: str


def classify_product_configuration_family(
    configuration: ProductConfiguration,
) -> ProductConfigurationFamilyClassification:
    family_key = str(configuration.family_id or "").strip().lower()

    if family_key in {"base_cabinet", "base cabinet"}:
        return ProductConfigurationFamilyClassification(
            family_id=configuration.family_id,
            executable_family=True,
            engineering_path="base_cabinet",
            reason="executable family for the current base cabinet path",
        )

    if family_key in {"wall_cabinet", "wall cabinet"}:
        return ProductConfigurationFamilyClassification(
            family_id=configuration.family_id,
            executable_family=True,
            engineering_path="wall_cabinet",
            reason="executable family for the current wall cabinet path",
        )

    if family_key in {"tall_cabinet", "tall cabinet"}:
        return ProductConfigurationFamilyClassification(
            family_id=configuration.family_id,
            executable_family=False,
            engineering_path=None,
            reason="catalog-only family; not executable through the current path",
        )

    return ProductConfigurationFamilyClassification(
        family_id=configuration.family_id,
        executable_family=False,
        engineering_path=None,
        reason="unknown family",
    )
