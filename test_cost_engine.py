from exports.bom_engine import BOMEngine
from costing.cost_engine import CostEngine

# هنا استدعِ أي SceneGraph موجود لديك
# أو نفس المسار الذي تستعمله لتوليد BOM

bom = BOMEngine.generate(builder.scene_graph)

report = CostEngine.generate(bom)

print("\n===== COST REPORT =====")

print("MDF Sheets :", round(report.mdf_sheets,2))
print("MDF Cost   :", round(report.mdf_cost,2))

print("Back Cost  :", round(report.back_cost,2))

print("PVC Meters :", round(report.pvc_meters,2))
print("PVC Cost   :", round(report.pvc_cost,2))

print("Total Cost :", round(report.total_cost,2))
print("Sell Price :", round(report.selling_price,2))
print("Profit     :", round(report.profit,2))
