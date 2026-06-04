from shared.issues import ValidationState
from manufacturing.extractor import ManufacturingExtractor
from validation.panel_spec_validator import PanelSpecValidator

class ManufacturingValidationService:

    @staticmethod
    def validate(scene_graph):

        specs = ManufacturingExtractor.extract(
            scene_graph
        )

        state = ValidationState()

        state.issues.extend(
            PanelSpecValidator().validate(
                specs
            )
        )

        return state
