import json
from pathlib import Path

from domain.anchors import MountFace


class HardwareCatalogLoader:

    @staticmethod
    def load(path):
        catalog_path = Path(path)
        if not catalog_path.exists():
            return {}

        try:
            with catalog_path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except (OSError, json.JSONDecodeError):
            return {}

        items = payload.get("items") if isinstance(payload, dict) else payload
        if not isinstance(items, list):
            return {}

        catalog = {}
        for item in items:
            spec = HardwareCatalogLoader._to_hardware_spec(item)
            if spec is not None:
                catalog[spec.sku] = spec
        return catalog

    @staticmethod
    def _to_hardware_spec(item):
        if not isinstance(item, dict):
            return None

        from domain.hardware_library import HardwareSpec

        host_holes = [
            HardwareCatalogLoader._to_hole_spec(hole)
            for hole in item.get("host_holes", [])
        ]
        host_holes = [hole for hole in host_holes if hole is not None]

        target_holes = [
            HardwareCatalogLoader._to_hole_spec(hole)
            for hole in item.get("target_holes", [])
        ]
        target_holes = [hole for hole in target_holes if hole is not None]

        return HardwareSpec(
            sku=item.get("sku", ""),
            manufacturer=item.get("manufacturer", ""),
            model=item.get("model", ""),
            revision=item.get("revision", ""),
            category=item.get("category", ""),
            hardware_family=item.get("hardware_family", ""),
            price=item.get("price", 0.0),
            host_holes=host_holes,
            target_holes=target_holes,
        )

    @staticmethod
    def _to_hole_spec(item):
        if not isinstance(item, dict):
            return None

        from domain.hardware_library import HoleSpec

        face_value = item.get("face", MountFace.FRONT)
        if isinstance(face_value, MountFace):
            face = face_value
        else:
            face_name = str(face_value).split(".")[-1]
            face = MountFace[face_name] if face_name in MountFace.__members__ else MountFace.FRONT

        return HoleSpec(
            diameter=item.get("diameter", 0.0),
            depth=item.get("depth", 0.0),
            face=face,
            axis=item.get("axis", "Z"),
            offset_x=item.get("offset_x", 0.0),
            offset_y=item.get("offset_y", 0.0),
            is_through_hole=item.get("is_through_hole", False),
        )
