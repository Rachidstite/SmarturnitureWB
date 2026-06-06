import csv
import os
import tempfile
import unittest

from exports.canonical_csv_exporter import (
    CanonicalCSVExporter
)

from manufacturing.canonical_cnc_row import (
    CanonicalCNCRow
)


class TestCanonicalCSVExporter(unittest.TestCase):

    def test_export_csv(self):

        rows = [
            CanonicalCNCRow(
                panel_id="PANEL_A",
                panel_role="SHELF",
                operation_type="DRILL",
                face="TOP",
                axis="X",
                x=10,
                y=20,
                z=5,
                diameter=8,
                depth=30,
                is_through=True,
                source="modern-core",
            )
        ]

        with tempfile.TemporaryDirectory() as tmpdir:

            csv_path = os.path.join(
                tmpdir,
                "canonical.csv"
            )

            CanonicalCSVExporter.export(
                rows,
                csv_path
            )

            with open(
                csv_path,
                "r",
                encoding="utf-8"
            ) as f:

                reader = csv.DictReader(f)

                data = list(reader)

        self.assertEqual(
            len(data),
            1
        )

        self.assertEqual(
            data[0]["Panel_ID"],
            "PANEL_A"
        )

        self.assertEqual(
            data[0]["Axis"],
            "X"
        )

        self.assertEqual(
            data[0]["Is_Through"],
            "1"
        )


if __name__ == "__main__":
    unittest.main()
