from exports.hardware_report import HardwareReportEngine

class DummyGraph:
    def all_nodes(self):
        return []

try:
    report = HardwareReportEngine.generate(DummyGraph())

    print("MINIFIX =", report.minifix_count)
    print("DOWEL   =", report.dowel_count)
    print("COST    =", report.hardware_cost)

except Exception as e:
    print("ERROR:", e)
