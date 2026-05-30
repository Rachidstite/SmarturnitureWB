import os
def apply(project_path):
    geom_path = os.path.join(project_path, "engine", "geometry_engine.py")
    with open(geom_path, "r") as f:
        content = f.read()
    if "from manufacturing.resolver import ManufacturingResolver" not in content:
        content = content.replace(
            "from validation.geometry_validator import GeometryValidator",
            "from validation.geometry_validator import GeometryValidator\nfrom manufacturing.resolver import ManufacturingResolver"
        )
        with open(geom_path, "w") as f:
            f.write(content)
