from manufacturing.factory_resource_catalog_service import (
    FactoryResourceCatalogService,
)
from manufacturing.factory_resource_report import FactoryResourceReport


class FactoryResourceBuilder:

    def __init__(self, catalog_service=None):
        self.catalog_service = catalog_service or FactoryResourceCatalogService()

    def build(self):
        catalog = self.catalog_service.load() or {}

        workers = catalog.get("workers", 0)
        cnc_machines = catalog.get("cnc_machines", 0)
        edge_banding_machines = catalog.get("edge_banding_machines", 0)
        assembly_stations = catalog.get("assembly_stations", 0)
        daily_work_hours = catalog.get("daily_work_hours", 0.0)
        workdays_per_week = catalog.get("workdays_per_week", 0)

        weekly_capacity_hours = (
            workers * daily_work_hours * workdays_per_week
        )

        return FactoryResourceReport(
            workers=workers,
            cnc_machines=cnc_machines,
            edge_banding_machines=edge_banding_machines,
            assembly_stations=assembly_stations,
            daily_work_hours=daily_work_hours,
            workdays_per_week=workdays_per_week,
            weekly_capacity_hours=weekly_capacity_hours,
        )
