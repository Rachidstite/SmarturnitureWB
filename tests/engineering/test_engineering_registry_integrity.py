from pathlib import Path

from validation.intelligence.engineering.engineering_rules_registry import (
    EngineeringRulesRegistry,
)


def test_all_engineering_rules_are_registered():

    rules_dir = Path(
        "validation/intelligence/engineering/rules"
    )

    ignored = {
        "carcass_rigidity_rule",
        "tall_cabinet_stability_rule",
        "basekick_span_rule",
    }

    expected = {
        p.stem
        for p in rules_dir.glob("*.py")
        if (
            p.stem != "__init__"
            and p.stem not in ignored
        )
    }

    registered = {
        type(rule).__name__
        for rule in (
            EngineeringRulesRegistry
            .get_rules()
        )
    }

    expected_class_names = {
        "".join(
            part.capitalize()
            for part in name.split("_")
        )
        for name in expected
    }

    missing = (
        expected_class_names
        - registered
    )

    assert not missing, (
        "Unregistered engineering rules: "
        f"{sorted(missing)}"
    )
