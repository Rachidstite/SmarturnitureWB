from validation.intelligence.connector_intent_rule import (
    ConnectorIntentRule,
)

from validation.intelligence.minifix_depth_rule import (
    MinifixDepthRule,
)

from validation.intelligence.confirmat_depth_rule import (
    ConfirmatDepthRule,
)


def get_hardware_rules():

    return [
        ConnectorIntentRule(),
        MinifixDepthRule(),
        ConfirmatDepthRule(),
    ]
