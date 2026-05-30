import os
from domain.assembly_graph import JoineryGraph, PartLabeler

class AssemblyManualExporter:
    """
    يولد دليل التجميع بصيغة HTML جاهز للطباعة للورشة.
    يعتمد بالكامل على الـ SceneGraph والـ JoineryGraph.
    """
    @staticmethod
    def export(scene_graph, joinery_graph: JoineryGraph, output_path: str):
        labeler = PartLabeler()
        nodes_dict = {}
        
        for node in getattr(scene_graph, 'physical_nodes', []):
            uid = node.identity.key if hasattr(node.identity, 'key') else str(node.identity)
            nodes_dict[uid] = node
            # تعيين الأكواد لكل قطعة
            labeler.assign_label(node)

        sequence = joinery_graph.get_assembly_sequence(list(nodes_dict.keys()))

        html = "<html><body style='font-family: sans-serif; background: #fff; color: #333; padding: 20px; max-width: 800px; margin: 0 auto;'>"
        html += "<h1 style='border-bottom: 3px solid #2980b9; color: #2c3e50;'>🛠️ Assembly Manual (Cabinet Vision Lite)</h1>"
        
        # 1. قائمة القطع (Bill of Materials - Simple)
        html += "<div style='background: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 30px; border: 1px solid #ddd;'>"
        html += "<h2>📦 Part Identification (Labels)</h2>"
        html += "<table style='width: 100%; border-collapse: collapse;'>"
        html += "<tr style='background: #e9ecef; border-bottom: 2px solid #ccc;'><th style='padding: 8px; text-align: left;'>Label</th><th style='padding: 8px; text-align: left;'>Part Name</th><th style='padding: 8px; text-align: left;'>Dimensions (mm)</th></tr>"
        
        for uid in sequence:
            node = nodes_dict[uid]
            # تجاوز الإكسسوارات مؤقتاً
            if "HARDWARE" in str(getattr(node, 'role', '')): continue
            
            lbl = labeler.assign_label(node)
            w = getattr(node, 'width', 0)
            h = getattr(node, 'height', 0)
            t = getattr(node, 'thickness', 0)
            html += f"<tr style='border-bottom: 1px solid #eee;'><td style='padding: 8px;'><b>{lbl}</b></td><td style='padding: 8px;'>{uid}</td><td style='padding: 8px;'>{int(w)} x {int(h)} x {int(t)}</td></tr>"
        html += "</table></div>"

        # 2. خطوات التجميع
        html += "<h2>⚙️ Assembly Steps</h2>"
        step_counter = 1
        
        # استخراج الوصلات لكل قطعة لتنظيم الخطوات
        target_to_edges = {}
        for edge in joinery_graph.edges:
            if edge.target_id not in target_to_edges:
                target_to_edges[edge.target_id] = []
            target_to_edges[edge.target_id].append(edge)

        for uid in sequence:
            if uid in target_to_edges:
                node = nodes_dict[uid]
                lbl = labeler.assign_label(node)
                edges = target_to_edges[uid]
                
                html += f"<div style='margin-bottom: 20px; padding: 15px; border-left: 4px solid #27ae60; background: #fdfdfd; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>"
                html += f"<h3 style='margin-top: 0; color: #27ae60;'>Step {step_counter}: Install [{lbl}]</h3>"
                html += "<ul style='font-size: 16px;'>"
                
                for edge in edges:
                    src_lbl = labeler.assign_label(nodes_dict[edge.source_id]) if edge.source_id in nodes_dict else f'[{edge.source_id}]'
                    html += f"<li>Attach <b>[{lbl}]</b> to <b>[{src_lbl}]</b> using <span style='background: #e1f5fe; padding: 2px 6px; border-radius: 3px; font-weight: bold;'>{edge.connector}</span>. {edge.instruction}</li>"
                
                html += "</ul></div>"
                step_counter += 1

        html += "</body></html>"
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✅ Assembly Manual generated at: {output_path}")
