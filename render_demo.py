from domain.builders import WardrobeBuilder
from gui.renderer import GeometryRenderer

cab = WardrobeBuilder(
    uid="DEMO",
    width=1200,
    height=2400,
    depth=600
)

cab.add_divider(600)

project = cab.build()

GeometryRenderer.render(project)

print("RENDER COMPLETE")
