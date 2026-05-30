from shared.contracts import CabinetParams
from core.material_manager import MaterialManager
class Cabinet:
    def __init__(self, params: CabinetParams = None): self.params = params or CabinetParams(); self.mat = MaterialManager(); self.sections = []
