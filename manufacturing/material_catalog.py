class MaterialCatalog:

    def __init__(self):
        self._materials = {}

    def add_material(self, key, material_spec):
        self._materials[key] = material_spec

    def get_material(self, key):
        return self._materials[key]

    def has_material(self, key):
        return key in self._materials

    def list_material_keys(self):
        return list(self._materials)

    @classmethod
    def from_library(cls, material_library):
        catalog = cls()
        catalog._materials = dict(material_library)
        return catalog
