from domain.core_types import NodeCategory
from domain.topology import Transform3D, BoundingBox

class SpatialQueryEngine:
    """محرك الاستعلام المكاني AABB (Axis-Aligned Bounding Box)"""
    def __init__(self, nodes):
        self.nodes = [n for n in nodes if getattr(n, 'category', None) == NodeCategory.PHYSICAL]

    def find_collisions(self) -> list:
        """يستخرج جميع القطع المتداخلة في الفضاء 3D (مهم للـ Assembly Validation)"""
        collisions = []
        for i, n1 in enumerate(self.nodes):
            for j, n2 in enumerate(self.nodes):
                if i >= j: continue
                
                # إعداد الـ Bounds محلياً للاستعلام
                b1_min = (n1.transform.x, n1.transform.y, n1.transform.z)
                b1_max = (n1.transform.x + n1.width, n1.transform.y + n1.depth if hasattr(n1, 'depth') else n1.transform.y + n1.thickness, n1.transform.z + n1.height)
                
                b2_min = (n2.transform.x, n2.transform.y, n2.transform.z)
                b2_max = (n2.transform.x + n2.width, n2.transform.y + n2.depth if hasattr(n2, 'depth') else n2.transform.y + n2.thickness, n2.transform.z + n2.height)

                if (b1_min[0] < b2_max[0] and b1_max[0] > b2_min[0] and
                    b1_min[1] < b2_max[1] and b1_max[1] > b2_min[1] and
                    b1_min[2] < b2_max[2] and b1_max[2] > b2_min[2]):
                    collisions.append((n1.identity.key, n2.identity.key))
        return collisions

    def get_nodes_at(self, x: float, y: float, z: float, tolerance: float = 1.0) -> list:
        """استعلام نقطي: ما هي القطع الموجودة في هذا الإحداثي؟ (مهم للـ CNC Drilling)"""
        found = []
        for n in self.nodes:
            if (n.transform.x - tolerance <= x <= n.transform.x + n.width + tolerance and
                n.transform.z - tolerance <= z <= n.transform.z + n.height + tolerance):
                found.append(n)
        return found
