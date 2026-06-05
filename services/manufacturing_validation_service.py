from shared.issues import ValidationState

from manufacturing.hybrid_extractor import (
    HybridManufacturingExtractor
)

from validation.validator_registry import VALIDATORS


class ManufacturingValidationService:

    @staticmethod
    def validate(scene_graph):

        specs = (
            HybridManufacturingExtractor.extract(
                scene_graph
            )
        )

        state = ValidationState()

        for validator in VALIDATORS:

            state.issues.extend(
                validator.validate(specs)
            )

        return state
