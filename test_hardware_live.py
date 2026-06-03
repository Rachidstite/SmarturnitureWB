from exports.hardware_report import HardwareReportEngine

report = HardwareReportEngine.generate(builder.scene_graph)

print()
print("===== HARDWARE REPORT =====")
print("MINIFIX =", report.minifix_count)
print("DOWEL   =", report.dowel_count)
print("COST    =", report.hardware_cost)
print("===========================")
