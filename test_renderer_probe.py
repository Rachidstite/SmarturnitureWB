from domain.builders import WardrobeBuilder

cab = WardrobeBuilder(
    uid="RENDER",
    width=1200,
    height=2400,
    depth=600
)

cab.add_divider(600)

project = cab.build()

print("Nodes:", len(project.graph.physical_nodes))

for n in project.graph.physical_nodes:
    print(n.identity.key, n.role)
