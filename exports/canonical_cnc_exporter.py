from manufacturing.canonical_cnc_mapper import (
    CanonicalCNCMapper
)


class CanonicalCNCExporter:

    @staticmethod
    def export_rows(panel_specs):

        rows = []

        for spec in panel_specs:

            for operation in getattr(
                spec,
                "unified_operations",
                []
            ):

                rows.append(
                    CanonicalCNCMapper
                    .from_unified_operation(
                        spec,
                        operation
                    )
                )

        return rows
