class ManufacturingWarningsAnalyzer:

    def analyze(self, package):
        warnings = []

        if not package.panels:
            warnings.append("No panels")
        if not package.materials:
            warnings.append("No materials")
        if not package.machining_operations:
            warnings.append("No machining operations")
        if not package.edge_operations:
            warnings.append("No edge operations")

        return warnings
