\
import csv
import os
from domain.builders import CabinetProject

class CNCExporter:
    """محرك تصدير بيانات التصنيع إلى صيغة محايدة (Neutral Manufacturing Format)"""
    
    @staticmethod
    def export_master_drilling_map(project: CabinetProject, filepath: str) -> str:
        # الهيكلية الصارمة والمحايدة التي تمنع التقيد بأي ماكينة حالياً
        headers = ['Panel_ID', 'Role', 'Face', 'X', 'Y', 'Diameter', 'Depth', 'Axis', 'Is_Through']
        
        rows = []
        for node in project.graph.physical_nodes:
            if hasattr(node, 'machining_ops') and node.machining_ops:
                for op in node.machining_ops:
                    role_str = node.role.value if hasattr(node.role, 'value') else str(node.role)
                    rows.append([
                        node.identity.key,
                        role_str,
                        op.face,
                        round(op.local_x, 2),
                        round(op.local_y, 2),
                        round(op.diameter, 2),
                        round(op.depth, 2),
                        getattr(op, 'axis', 'Z'), # المحور الميكانيكي الحاسم
                        int(getattr(op, 'is_through', False)) # 0 أو 1 لسهولة القراءة بالـ CAM
                    ])
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
            
        return filepath
