from validation.intelligence.engineering.engineering_rules_registry import (
    EngineeringRulesRegistry,
)


def test_registry_contains_expected_rules():

    names = {
        rule.__class__.__name__
        for rule in (
            EngineeringRulesRegistry
            .get_rules()
        )
    }

    expected = {
        "ShelfDeflectionRule",
        "DividerBucklingRule",
        "DoorSagRule",
        "HangingCabinetLoadRule",
        "WideDrawerDeflectionRule",
        "CountertopSpanRule",
        "LongDoorHingeRule",
    }

    assert expected.issubset(names)
