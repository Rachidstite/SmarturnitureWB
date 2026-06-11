from cost_intelligence.offcut_report import OffcutReport


class OffcutReportBuilder:

    def build(
        self,
        offcuts,
    ):
        return OffcutReport(
            offcuts=offcuts,
            total_offcuts=len(offcuts),
            reusable_offcuts=sum(
                1
                for offcut in offcuts
                if offcut.reusable
            ),
            total_offcut_area=sum(
                offcut.area
                for offcut in offcuts
            ),
            largest_offcut_area=max(
                (
                    offcut.area
                    for offcut in offcuts
                ),
                default=0,
            ),
        )
