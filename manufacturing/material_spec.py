from dataclasses import dataclass

@dataclass
class MaterialSpec:
    """مواصفات خامة تصنيعية."""
    name: str               # "MDF_MR_18MM", "HDF_3MM", "MELAMINE_WHITE_18MM"
    thickness: float        # السماكة الاسمية (mm)
    density: float = 750.0  # kg/m³
    sheet_width: float = 1830.0   # عرض اللوح الخام (mm)
    sheet_height: float = 3660.0  # طول اللوح الخام (mm)
    edge_band_default: str = "ABS_1MM"  # شريط اللصق الافتراضي
    price_per_m2: float = 0.0   # سعر المتر المربع

# مكتبة خامات أساسية
MATERIAL_LIBRARY = {
    "MDF_18MM": MaterialSpec("MDF_MR_18MM", 18.0, 750, 1830, 3660, "ABS_1MM"),
    "MDF_8MM": MaterialSpec("MDF_MR_8MM", 8.0, 750, 1830, 3660, "ABS_1MM"),
    "HDF_3MM": MaterialSpec("HDF_3MM", 3.0, 900, 1830, 3660, "NONE"),
    "MELAMINE_WHITE_18MM": MaterialSpec("Melamine White", 18.0, 680, 1830, 3660, "ABS_1MM"),
}
