from core.qt_compat import QtWidgets; from shared.enums import Domain
class IssuePresenter(QtWidgets.QWidget):
    def __init__(self):
        super().__init__(); layout = QtWidgets.QVBoxLayout(self); layout.setContentsMargins(0,5,0,0)
        self.text_edit = QtWidgets.QTextEdit(); self.text_edit.setReadOnly(True); self.text_edit.setMaximumHeight(200); self.text_edit.hide(); layout.addWidget(self.text_edit)
    def display_issues(self, issues: list):
        if not issues: self.text_edit.hide(); return
        self.text_edit.show()
        grouped = {}
        for issue in issues:
            domain = issue.domain if hasattr(issue, 'domain') else Domain.GENERAL; grouped.setdefault(domain, []).append(issue)
        html = "<h4 style='margin-bottom:5px;'>Validation Results:</h4>"
        for domain, items in grouped.items():
            html += f"<p style='font-weight:bold;margin:8px 0 2px 0;'>=== {domain.value} ==="
            html += "<ul style='margin-top:0;'>"
            for issue in items:
                color = "#D32F2F" if issue.level == "ERROR" else "#F57C00"; icon = "❌" if issue.level == "ERROR" else "⚠️"
                html += f"<li style='color:{color};margin-bottom:3px;'>{icon} <b>[{issue.code}]</b> {issue.message}</li>"
            html += "</ul>"
        self.text_edit.setHtml(html)
