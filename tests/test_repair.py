"""Demo version test."""

import pytest

from bibliomancer import repair
from bibliomancer.enricher import RULES


@pytest.mark.parametrize("rule", RULES)
def test_repair(rule):
    for rule_test in rule["tests"]:
        print("TEST", rule_test)
        assert repair(rule_test["input"], rules=[rule["name"]]) == rule_test["output"]
