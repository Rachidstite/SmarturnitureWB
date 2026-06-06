import csv
import os


class CanonicalCSVExporter:

    HEADERS = [
        "Panel_ID",
        "Role",
        "Operation_Type",
        "Face",
        "Axis",
        "X",
        "Y",
        "Z",
        "Diameter",
        "Depth",
        "Is_Through",
        "Source",
    ]

    @staticmethod
    def export(rows, filepath):

        os.makedirs(
            os.path.dirname(filepath),
            exist_ok=True
        )

        with open(
            filepath,
            "w",
            newline="",
            encoding="utf-8"
        ) as f:

            writer = csv.writer(f)

            writer.writerow(
                CanonicalCSVExporter.HEADERS
            )

            for row in rows:

                writer.writerow([
                    row.panel_id,
                    row.panel_role,
                    row.operation_type,
                    row.face,
                    row.axis,
                    row.x,
                    row.y,
                    row.z,
                    row.diameter,
                    row.depth,
                    int(row.is_through),
                    row.source,
                ])

        return filepath
