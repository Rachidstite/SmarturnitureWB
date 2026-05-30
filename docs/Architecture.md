# SMART CABINET PRO - System Architecture

## 1. Core Philosophy (المبادئ الأساسية)
- **Furniture = Production Data**: النظام يولد بيانات تصنيع دقيقة.
- **Strict Logic/GUI Separation**: النواة تعمل بشكل مستقل.
- **FreeCAD Part Module Dependency**: اعتماد صارم على وحدة Part.
- **Associative Math**: إحداثيات محسوبة ديناميكياً.

## 2. Pipeline Architecture (مسار البيانات)
User -> WardrobeBuilder -> Topology Engine -> SceneGraph -> Rules Engine -> Compiler -> Validation Shield -> Export Layer

## 3. Core Modules
- **SceneGraph**: قاعدة بيانات O(1).
- **Compiler**: تحويل النوايا إلى عمليات CNC.
- **Validation Shield**: حماية الماكينة مكانياً.