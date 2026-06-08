from core.qt_compat import QtWidgets


class ManufacturingDashboardWidget(
    QtWidgets.QGroupBox
):

    def __init__(self):
        super().__init__(
            "Manufacturing Intelligence"
        )

        layout = QtWidgets.QFormLayout(self)

        self.lbl_score = QtWidgets.QLabel("-")
        self.lbl_grade = QtWidgets.QLabel("-")
        self.lbl_warnings = QtWidgets.QLabel("-")
        self.lbl_recommendations = QtWidgets.QLabel("-")
        self.txt_recommendations = QtWidgets.QPlainTextEdit()
        self.txt_recommendations.setReadOnly(True)

        self.lbl_cost_impacts = QtWidgets.QLabel("-")
        self.lbl_export = QtWidgets.QLabel("-")

        layout.addRow(
            "Score",
            self.lbl_score,
        )

        layout.addRow(
            "Grade",
            self.lbl_grade,
            )

        layout.addRow(
            "Warnings",
            self.lbl_warnings,
        )

        layout.addRow(
            "Recommendations",
            self.lbl_recommendations,
        )

        layout.addRow(
            "Recommendation Details",
            self.txt_recommendations,
        )

        layout.addRow(
            "Cost Impacts",
            self.lbl_cost_impacts,
        )

        layout.addRow(
            "Can Export",
            self.lbl_export,
        )

    def update_state(
        self,
        state,
    ):

        print("\nUI UPDATE")
        print(
            "recommendation_count =",
            state.recommendation_count
        )
        print(
            "recommendations =",
            getattr(
                state,
                "recommendations",
                None
            )
        )
        self.lbl_score.setText(
            str(state.score)
        )

        self.lbl_grade.setText(
            state.grade
        )

        self.lbl_warnings.setText(
            str(state.warning_count)
        )

        self.lbl_recommendations.setText(
            str(state.recommendation_count)
        )

        self.txt_recommendations.setPlainText(
            "\n".join(
                getattr(
                    state,
                    "recommendations",
                    []
                )
            )
        )

        self.lbl_cost_impacts.setText(
            str(state.cost_impact_count)
        )

        self.lbl_export.setText(
            "YES" if state.can_export
            else "NO"
        )
