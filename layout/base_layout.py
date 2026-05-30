from abc import ABC, abstractmethod
from .layout_context import LayoutContext; from .layout_result import LayoutResult
class DrawerLayoutStrategy(ABC):
    @abstractmethod
    def resolve(self, context: LayoutContext) -> LayoutResult: pass
