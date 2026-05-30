import os

class SVGNestingExporter:
    """
    يولد خريطة قص صناعية (Shop-floor Cutting Map)
    مبنية على الـ Cut Tree (Rip Cuts & Cross Cuts)
    """
    
    @staticmethod
    def export(nesting_results, output_path: str, sheet_w=2440.0, sheet_h=1220.0, trim=10.0):
        scale = 0.4 
        svg = "<html><body style='font-family: sans-serif; background: #eef2f3; padding: 20px;'>"
        svg += "<h1>🏭 SMART CABINET PRO - Shop-Floor Cutting Map</h1>"
        
        for material, sheets in nesting_results.items():
            svg += f"<h2 style='color: #2c3e50; border-bottom: 2px solid #bdc3c7;'>🪵 Material: {material}</h2>"
            
            for sheet in sheets:
                yield_pct = (sheet.used_area / (sheet_w * sheet_h)) * 100
                svg += f"<h3>Sheet {sheet.sheet_id} | Yield: {yield_pct:.1f}%</h3>"
                
                sw, sh = sheet_w * scale, sheet_h * scale
                svg += f'<svg width="{sw}" height="{sh}" style="background: #fff; border: 2px solid #333; margin-bottom: 40px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1);">'
                
                # 1. رسم Trim Cuts (قص التنظيف - خطوط متقطعة رمادية)
                t = trim * scale
                svg += f'<rect x="{t}" y="{t}" width="{sw - 2*t}" height="{sh - 2*t}" fill="none" stroke="#95a5a6" stroke-width="1" stroke-dasharray="4,4" />'
                svg += f'<text x="5" y="{t-2}" font-size="9" fill="#7f8c8d">Trim 10mm</text>'
                
                rip_counter = 1
                cross_counter = 1
                
                for strip in sheet.strips:
                    # 2. استخراج الفراغات (Offcuts) القابلة لإعادة الاستخدام في نهاية الشريحة
                    if strip.parts:
                        last_part = strip.parts[-1]
                        remaining_w = (sheet_w - trim) - last_part.cross_cut_x
                        if remaining_w > 100: # Offcut قابل للاستخدام
                            ox, oy = last_part.cross_cut_x * scale, strip.y_start * scale
                            ow, oh = remaining_w * scale, strip.height * scale
                            svg += f'<rect x="{ox}" y="{oy}" width="{ow}" height="{oh}" fill="#e8f5e9" stroke="#2e7d32" stroke-width="1" />'
                            svg += f'<text x="{ox + ow/2}" y="{oy + oh/2}" font-size="10" text-anchor="middle" fill="#2e7d32" font-weight="bold">OFFCUT ({int(remaining_w)}x{int(strip.height)})</text>'

                    # 3. رسم القطع والـ Cross Cuts (أزرق)
                    for p in strip.parts:
                        x, y = p.x * scale, p.y * scale
                        w, h = p.placed_width * scale, p.placed_height * scale
                        
                        # تلوين القطع مع توضيح اتجاه العروق (Grain)
                        fill = "#fff"
                        svg += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="#34495e" stroke-width="1" />'
                        
                        # اسم القطعة
                        svg += f'<text x="{x + w/2}" y="{y + h/2 - 6}" font-size="10" text-anchor="middle" fill="#2c3e50" font-weight="bold">{p.part.semantic_name}</text>'
                        
                        # اتجاه العروق (إذا كان لا يمكن تدويره يعني أن له عروق)
                        if not p.part.can_rotate:
                            grain_dir = "↕" if not p.rotated else "↔"
                            svg += f'<text x="{x + w/2}" y="{y + h/2 + 8}" font-size="12" text-anchor="middle" fill="#7f8c8d">{grain_dir}</text>'
                        
                        # خط الـ Cross Cut (أزرق)
                        cc_x = p.cross_cut_x * scale
                        svg += f'<line x1="{cc_x}" y1="{strip.y_start * scale}" x2="{cc_x}" y2="{strip.rip_cut_y * scale}" stroke="#2980b9" stroke-width="2" />'
                        svg += f'<text x="{cc_x + 2}" y="{y + 12}" font-size="9" fill="#2980b9">C{cross_counter} @ {int(p.cross_cut_x)}</text>'
                        cross_counter += 1

                    # 4. رسم الـ Rip Cuts (أحمر سميك)
                    ry = strip.rip_cut_y * scale
                    svg += f'<line x1="0" y1="{ry}" x2="{sw}" y2="{ry}" stroke="#c0392b" stroke-width="2.5" />'
                    svg += f'<text x="5" y="{ry - 4}" font-size="11" fill="#c0392b" font-weight="bold">RIP {rip_counter} @ {int(strip.rip_cut_y)}</text>'
                    rip_counter += 1
                
                svg += "</svg>"
                
        svg += "</body></html>"
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(svg)
        print(f"✅ Shop-floor SVG Map generated at: {output_path}")
