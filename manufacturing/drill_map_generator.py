from collections import defaultdict

class DrillMapGenerator:

    @staticmethod
    def generate(panel_specs):

        drill_map = defaultdict(list)

        for panel in panel_specs:

            if not panel.cnc_operations:
                continue

            for op in panel.cnc_operations:
                drill_map[panel.identity].append(op)

        return dict(drill_map)
