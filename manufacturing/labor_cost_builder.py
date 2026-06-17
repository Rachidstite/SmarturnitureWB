from manufacturing.labor_cost_report import LaborCostReport


class LaborCostBuilder:

    def __init__(
        self,
        cnc_hourly_rate=0.0,
        drilling_hourly_rate=0.0,
        edge_banding_hourly_rate=0.0,
        assembly_hourly_rate=0.0,
        currency="MAD",
    ):
        self.cnc_hourly_rate = cnc_hourly_rate
        self.drilling_hourly_rate = drilling_hourly_rate
        self.edge_banding_hourly_rate = edge_banding_hourly_rate
        self.assembly_hourly_rate = assembly_hourly_rate
        self.currency = currency

    def build(self, manufacturing_duration_report):
        cnc_labor_cost = self._minutes_to_cost(
            manufacturing_duration_report.estimated_cnc_minutes,
            self.cnc_hourly_rate,
        )
        drilling_labor_cost = self._minutes_to_cost(
            manufacturing_duration_report.estimated_drilling_minutes,
            self.drilling_hourly_rate,
        )
        edge_banding_labor_cost = self._minutes_to_cost(
            manufacturing_duration_report.estimated_edge_banding_minutes,
            self.edge_banding_hourly_rate,
        )
        assembly_labor_cost = self._minutes_to_cost(
            manufacturing_duration_report.estimated_assembly_minutes,
            self.assembly_hourly_rate,
        )

        total_labor_cost = (
            cnc_labor_cost
            + drilling_labor_cost
            + edge_banding_labor_cost
            + assembly_labor_cost
        )

        warnings = list(getattr(manufacturing_duration_report, "warnings", []) or [])
        if all(
            rate == 0.0
            for rate in [
                self.cnc_hourly_rate,
                self.drilling_hourly_rate,
                self.edge_banding_hourly_rate,
                self.assembly_hourly_rate,
            ]
        ):
            warnings.append("Labor hourly rates are defaulting to zero")

        return LaborCostReport(
            cnc_labor_cost=cnc_labor_cost,
            drilling_labor_cost=drilling_labor_cost,
            edge_banding_labor_cost=edge_banding_labor_cost,
            assembly_labor_cost=assembly_labor_cost,
            total_labor_cost=total_labor_cost,
            currency=self.currency,
            warnings=warnings,
        )

    @staticmethod
    def _minutes_to_cost(minutes, hourly_rate):
        return (minutes / 60.0) * hourly_rate
