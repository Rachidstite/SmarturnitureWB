from validation.intelligence.engineering.engineering_assembly_rules_registry import (
    EngineeringAssemblyRulesRegistry,
)


def test_registry_returns_rules():

    rules = (
        EngineeringAssemblyRulesRegistry
        .get_rules()
    )

    assert len(rules) >= 2
