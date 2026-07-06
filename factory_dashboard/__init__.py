# ──────────────────────────────────────────────────────────────────────
# SmartFurnitureWB — Factory Dashboard Read Models
#
# Foundation for a future Factory Dashboard.
#
# This is NOT a graphical dashboard.
# This is NOT Qt work.
# This is NOT rendering.
# This is NOT charts.
# This is NOT widgets.
#
# This package creates only immutable dashboard read models.
#
# The dashboard aggregates existing FOI read models without
# creating new business logic. It never:
# - calculates readiness, blocking, recommendations, or decisions
# - duplicates FOI business rules
# - imports from domain, manufacturing, cost, or commercial modules
# - imports FreeCAD or Qt
# ──────────────────────────────────────────────────────────────────────

from .dashboard_read_model import (
    FactoryDashboardReadModel,
    FactoryDashboardSection,
    build_factory_dashboard_read_model,
    build_manufacturing_render_dashboard_section,
)

__all__ = [
    "FactoryDashboardSection",
    "FactoryDashboardReadModel",
    "build_factory_dashboard_read_model",
    "build_manufacturing_render_dashboard_section",
]
