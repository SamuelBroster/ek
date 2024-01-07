import logging
from collections.abc import Callable
from dataclasses import dataclass

from pydantic.fields import FieldInfo

from ek.rules.results import Result

_LOG = logging.getLogger(__name__)

ModelFields = dict[str, FieldInfo]
ModelRuleFunction = Callable[[ModelFields], Result]
Results = dict["ModelRule", Result]


class InvalidRuleError(Exception):
    pass


@dataclass(frozen=True, slots=True, kw_only=True)
class ModelRule:
    check: ModelRuleFunction
    dependencies: "frozenset[ModelRule]"

    def __str__(self) -> str:
        return self.check.__name__


def execute_rules(rules: set[ModelRule], fields: ModelFields) -> Results:
    results: Results = {}
    if invalid_rules := [
        rule for rule in rules if not rule.dependencies.issubset(rules)
    ]:
        raise InvalidRuleError(f"Invalid rules found: {invalid_rules}")
    return _execute_rules_recursively(rules, fields, results)


def _execute_rules_recursively(
    rules: set[ModelRule], fields: ModelFields, current_results: Results
) -> Results:
    (success, _), unexecuted = _executed_rules(rules, current_results)
    while rules_to_execute := _rules_to_execute(unexecuted, success):
        for rule in rules_to_execute:
            current_results[rule] = rule.check(fields)
        (success, _), unexecuted = _executed_rules(rules, current_results)
    return current_results


def _rules_to_execute(
    unexecuted_rules: set[ModelRule], successfully_executed: set[ModelRule]
) -> set[ModelRule]:
    if duplicates := unexecuted_rules.intersection(successfully_executed):
        raise AssertionError(f"Duplicate rules found: {duplicates}")

    rules_to_execute = {
        rule
        for rule in unexecuted_rules
        if rule.dependencies.issubset(successfully_executed)
    }
    _LOG.debug(
        "Rules to execute: %s (unexecuted: %s, executed: %s)",
        ", ".join([str(rule) for rule in rules_to_execute]),
        ", ".join([str(rule) for rule in unexecuted_rules]),
        ", ".join([str(rule) for rule in successfully_executed]),
    )
    return rules_to_execute


def _executed_rules(
    rules: set[ModelRule], results: Results
) -> tuple[tuple[set[ModelRule], set[ModelRule]], set[ModelRule]]:
    executed = rules.intersection(results.keys())
    success = {rule for rule in executed if results[rule].success}
    failure = executed.difference(success)
    unexecuted = rules.difference(executed)
    return ((success, failure), unexecuted)
