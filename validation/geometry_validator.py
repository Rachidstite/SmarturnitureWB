from shared.issues import GeometryIssue; from shared.enums import Domain
class GeometryValidator:
    def validate(self, resolved_sections, mat) -> list:
        issues = []
        for i, r in enumerate(resolved_sections):
            if r.drawer_box_width < 100: issues.append(GeometryIssue("WARNING", "DRAWER_TOO_NARROW", f"Section {i+1}: Drawer box width ({r.drawer_box_width:.1f}mm) is very narrow.", i, domain=Domain.GEOMETRY))
            for shelf in r.shelves:
                if shelf.depth < 50: issues.append(GeometryIssue("WARNING", "SHELF_TOO_SHALLOW", f"Section {i+1}: Shelf depth ({shelf.depth:.1f}mm) is below minimum.", i, domain=Domain.GEOMETRY))
        return issues
