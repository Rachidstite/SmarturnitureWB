from scene_graph.node import SceneNode
from scene_graph.renderer import SceneRenderer

class RendererRegistry:
    """يُسجل استراتيجيات الرسم حسب الدور."""
    _renderers = {}

    @classmethod
    def register(cls, role: str, renderer_func):
        cls._renderers[role] = renderer_func

    @classmethod
    def render(cls, node: SceneNode, renderer: SceneRenderer):
        func = cls._renderers.get(node.role)
        if func:
            func(node, renderer)
        else:
            # الرسم الافتراضي للألواح البسيطة
            renderer._render_simple_panel(node)
