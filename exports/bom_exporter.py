import csv
import os
from collections import defaultdict
from domain.builders import CabinetProject
from domain.rules_engine import RuleContext
from domain.hardware_library import HardwareRegistry

class BOMExporter:
    """محرك تصدير فاتورة الإكسسوارات (Bill of Materials)"""
    
    @staticmethod
    def export_hardware_bom(project: CabinetProject, context: RuleContext, filepath: str) -> str:
        registry = HardwareRegistry()
        bom_counts = defaultdict(int)
        
        # 1. تجميع الكميات بناءً على النوايا والسياق (RuleContext)
        for placement in getattr(project, 'placements', []):
            sku = context.hardware_profile.get(placement.hardware_intent)
            if sku:
                bom_counts[sku] += 1
                

        # 2. تجهيز البيانات للطباعة
        rows = []
        for sku, count in bom_counts.items():
            spec = registry.get_hardware(sku)
            # ⚡ المعمارية النظيفة: الاعتماد على الكيان نفسه لتعريف اسمه
            item_name = spec.display_name if spec else "Unknown Hardware"
            manufacturer = spec.manufacturer if spec else "Unknown"
            rows.append([sku, item_name, manufacturer, count])
            
        # 3. التصدير إلى CSV
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['SKU', 'Item Name', 'Manufacturer', 'Quantity'])
            writer.writerows(rows)
        return filepath
