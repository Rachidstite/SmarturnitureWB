from engine.diff_engine import DiffResult
from engine.object_registry import PersistentObjectRegistry
from engine.policies import ShapeReplacePolicy, TransformOnlyPolicy, VisualOnlyPolicy

class IncrementalRenderer:
    """محرك التحديث الذي يوجه التغييرات الدلالية للسياسة المناسبة"""
    def __init__(self, document, registry, object_registry: PersistentObjectRegistry):
        self.doc = document
        self.registry = registry
        self.obj_registry = object_registry

    def apply_diff(self, diff_result: DiffResult, new_graph):
        if not diff_result.requires_update: return

        for uid in diff_result.removed: 
            self._delete_object(uid)
        
        for uid in diff_result.added:
            node = new_graph.get_node(uid)
            if node: self._create_object(node)

        # ⚡ Policy Dispatcher Core (توزيع المهام بذكاء)
        for uid, changes in diff_result.modified.items():
            node = new_graph.get_node(uid)
            if node: self._dispatch_update(node, changes)

        self.doc.recompute()

    def _dispatch_update(self, node, changes):
        uid = node.identity.key if hasattr(node.identity, 'key') else str(node.identity)
        fc_obj = self.obj_registry.resolve(self.doc, uid)
        
        if not fc_obj:
            self._create_object(node)
            return

        renderer_cls = self.registry.get(getattr(node, 'role', None))
        if not renderer_cls: return

        # التوجيه بناءً على المعنى (Semantics)
        if changes.requires_rebuild:
            # تحديث كامل للهندسة
            ShapeReplacePolicy.apply_update(fc_obj, node, renderer_cls)
        elif changes.transform_changed:
            # تحديث المكان فقط (لا يوجد حساب هندسي مكلف)
            TransformOnlyPolicy.apply_update(fc_obj, node, renderer_cls)
            if changes.visual_changed:
                VisualOnlyPolicy.apply_update(fc_obj, node, renderer_cls)
        elif changes.visual_changed:
            # تحديث اللون والمادة فقط
            VisualOnlyPolicy.apply_update(fc_obj, node, renderer_cls)

    def _delete_object(self, uid: str):
        fc_obj = self.obj_registry.resolve(self.doc, uid)
        if fc_obj:
            self.doc.removeObject(fc_obj.Name)
            self.obj_registry.purge(uid)

    def _create_object(self, node):
        uid = node.identity.key if hasattr(node.identity, 'key') else str(node.identity)
        renderer_cls = self.registry.get(getattr(node, 'role', None))
        if renderer_cls and hasattr(renderer_cls, 'create_new'):
            fc_obj = renderer_cls.create_new(self.doc, node)
            if fc_obj: 
                self.obj_registry.register(uid, fc_obj)
