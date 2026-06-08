from types import SimpleNamespace

from validation.intelligence.engineering.engineering_assembly_rule_engine import (
    EngineeringAssemblyRuleEngine,
)

from validation.intelligence.engineering.engineering_assembly_rules_registry import (
    EngineeringAssemblyRulesRegistry,
)


def test_assembly_rules_generate_results():

    scene_graph = SimpleNamespace(
        physical_nodes=[]
    )

    results = (
        EngineeringAssemblyRuleEngine(
            rules=
            EngineeringAssemblyRulesRegistry.get_rules()
        )
        .validate(scene_graph)
    )

    assert len(results) > 0
