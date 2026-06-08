from core.qt_compat import QtWidgets


class ManufacturingIntelligenceDetailsWidget(
    QtWidgets.QGroupBox
):

    def __init__(self):
        super().__init__(
            "Manufacturing Details"
        )

        layout = QtWidgets.QVBoxLayout(self)

        self.text = QtWidgets.QTextEdit()
        self.text.setReadOnly(True)

        layout.addWidget(self.text)

    def update_report(
        self,
        report,
    ):
        html = ""

        html += "<h3>Warnings</h3>"

        for item in getattr(
            report,
            "warnings",
            [],
        ):
            html += (
                f"<p>⚠ {item.message}</p>"
            )

        html += "<h3>Recommendations</h3>"

        for item in getattr(
            report,
            "recommendations",
            [],
        ):
            html += (
                f"<p>💡 {item.message}</p>"
            )

        html += "<h3>Cost Impacts</h3>"

        for item in getattr(
            report,
            "cost_impacts",
            [],
        ):
            html += (
                f"<p>💰 {item.description} (Saving: {item.estimated_savings})</p>"
            )

        self.text.setHtml(html)
