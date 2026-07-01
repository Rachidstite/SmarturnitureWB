from __future__ import annotations

from dataclasses import dataclass, field

from domain.product_family import ProductFamily


@dataclass(frozen=True)
class ProductFamilyRegistry:
    product_families: dict[str, ProductFamily] = field(default_factory=dict)

    def with_family(self, family: ProductFamily) -> "ProductFamilyRegistry":
        updated = dict(self.product_families)
        updated[family.family_id] = family
        return ProductFamilyRegistry(product_families=updated)

    def get(self, family_id: str) -> ProductFamily | None:
        return self.product_families.get(family_id)

    def contains(self, family_id: str) -> bool:
        return family_id in self.product_families
