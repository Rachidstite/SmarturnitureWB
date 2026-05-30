import os
import csv
from collections import defaultdict
from exports.production_engine import CutlistItem

class CSVExporter:
    """
    محرك تصدير بيانات القص إلى صيغة CSV متوافقة مع ورش الـ MDF
    وبرامج التحسين (CutList Optimizer, MaxCut).
    """
    
    @staticmethod
    def export(cutlist, output_path: str):
        # 1. تجميع القطع المتطابقة (Grouping)
        grouped_items = defaultdict(lambda: {"qty": 0, "item": None})
        
        for item in cutlist:
            # المفتاح يعتمد على المقاسات والمادة والحواف لتجميع القطع المتطابقة تماماً
            # نتجاهل الـ Identity هنا لأننا نريد جمع "رفين" نفس المقاس في سطر واحد
            key = (
                item.material, 
                round(item.cut_width, 1), 
                round(item.cut_height, 1), 
                item.grain_direction,
                item.edge_bands.get("TOP"),
                item.edge_bands.get("BOTTOM"),
                item.edge_bands.get("LEFT"),
                item.edge_bands.get("RIGHT")
            )
            grouped_items[key]["qty"] += 1
            grouped_items[key]["item"] = item

        # 2. كتابة ملف الـ CSV
        # نستخدم utf-8-sig لضمان قراءة Excel للأحرف بشكل صحيح
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, mode='w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            
            # الهيدر الصناعي القياسي
            writer.writerow([
                "Part Name", 
                "Material", 
                "Quantity", 
                "Cut Length", 
                "Cut Width", 
                "Finished Length", 
                "Finished Width", 
                "Thickness", 
                "Grain Direction",
                "Edge Top", 
                "Edge Bottom", 
                "Edge Left", 
                "Edge Right"
            ])
            
            for group in grouped_items.values():
                qty = group["qty"]
                it = group["item"]
                
                writer.writerow([
                    it.identity,  # إذا تم تجميع عدة قطع، سيأخذ اسم أول قطعة كمرجع
                    it.material,
                    qty,
                    round(it.cut_height, 1),  # Length is usually the longer side or Y axis
                    round(it.cut_width, 1),
                    round(it.finished_height, 1),
                    round(it.finished_width, 1),
                    round(it.thickness, 1),
                    it.grain_direction,
                    it.edge_bands.get("TOP", ""),
                    it.edge_bands.get("BOTTOM", ""),
                    it.edge_bands.get("LEFT", ""),
                    it.edge_bands.get("RIGHT", "")
                ])
                
        print(f"✅ Cutlist exported successfully to: {output_path}")
