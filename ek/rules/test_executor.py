import pytest

from ek.rules.executor import InvalidRuleError, ModelFields, ModelRule, execute_rules
from ek.rules.results import SUCCESS, Result, failure

FAIL_TYPE1 = failure("Type 1 failure")


def always_succeed_check(fields: ModelFields) -> Result:
    return SUCCESS


def always_fail_check(fields: ModelFields) -> Result:
    return FAIL_TYPE1


no_deps_always_succeed_rule = ModelRule(
    check=always_succeed_check, dependencies=frozenset()
)
no_deps_always_fail_rule = ModelRule(check=always_fail_check, dependencies=frozenset())

always_success_with_successful_deps = ModelRule(
    check=always_succeed_check, dependencies=frozenset({no_deps_always_succeed_rule})
)
always_success_with_unsuccessful_deps = ModelRule(
    check=always_succeed_check, dependencies=frozenset({no_deps_always_fail_rule})
)

always_success_with_unsuccessful_mixed_deps = ModelRule(
    check=always_succeed_check,
    dependencies=frozenset({no_deps_always_fail_rule, no_deps_always_succeed_rule}),
)

always_success_with_nested_successful_deps = ModelRule(
    check=always_succeed_check,
    dependencies=frozenset({always_success_with_successful_deps}),
)
always_success_with_nested_unsuccessful_deps = ModelRule(
    check=always_succeed_check,
    dependencies=frozenset({always_success_with_unsuccessful_deps}),
)

always_success_with_nested_mixed_successful_deps = ModelRule(
    check=always_succeed_check,
    dependencies=frozenset(
        {always_success_with_successful_deps, no_deps_always_succeed_rule}
    ),
)
always_success_with_nested_mixed_unsuccessful_deps = ModelRule(
    check=always_succeed_check,
    dependencies=frozenset(
        {
            no_deps_always_succeed_rule,
            always_success_with_unsuccessful_deps,
            no_deps_always_fail_rule,
        }
    ),
)


def has_expected_fields_check(fields: ModelFields) -> Result:
    if "expected_fields" not in fields:
        return FAIL_TYPE1
    return SUCCESS


has_expected_fields_rule = ModelRule(
    check=has_expected_fields_check, dependencies=frozenset()
)


@pytest.mark.parametrize(
    ("rules", "result"),
    [
        ({no_deps_always_succeed_rule}, {no_deps_always_succeed_rule: SUCCESS}),
        ({no_deps_always_fail_rule}, {no_deps_always_fail_rule: FAIL_TYPE1}),
        (
            {no_deps_always_succeed_rule, no_deps_always_fail_rule},
            {
                no_deps_always_succeed_rule: SUCCESS,
                no_deps_always_fail_rule: FAIL_TYPE1,
            },
        ),
        (
            {no_deps_always_succeed_rule, always_success_with_successful_deps},
            {
                no_deps_always_succeed_rule: SUCCESS,
                always_success_with_successful_deps: SUCCESS,
            },
        ),
        (
            {no_deps_always_fail_rule, always_success_with_unsuccessful_deps},
            {
                no_deps_always_fail_rule: FAIL_TYPE1,
            },
        ),
        (
            {
                always_success_with_unsuccessful_mixed_deps,
                no_deps_always_fail_rule,
                no_deps_always_succeed_rule,
            },
            {
                no_deps_always_fail_rule: FAIL_TYPE1,
                no_deps_always_succeed_rule: SUCCESS,
            },
        ),
        (
            {
                always_success_with_nested_successful_deps,
                no_deps_always_succeed_rule,
                always_success_with_successful_deps,
            },
            {
                no_deps_always_succeed_rule: SUCCESS,
                always_success_with_successful_deps: SUCCESS,
                always_success_with_nested_successful_deps: SUCCESS,
            },
        ),
        (
            {
                no_deps_always_fail_rule,
                always_success_with_nested_unsuccessful_deps,
                always_success_with_unsuccessful_deps,
            },
            {
                no_deps_always_fail_rule: FAIL_TYPE1,
            },
        ),
        (
            {
                always_success_with_nested_mixed_successful_deps,
                always_success_with_successful_deps,
                no_deps_always_succeed_rule,
                no_deps_always_fail_rule,
            },
            {
                no_deps_always_fail_rule: FAIL_TYPE1,
                always_success_with_successful_deps: SUCCESS,
                no_deps_always_succeed_rule: SUCCESS,
                always_success_with_nested_mixed_successful_deps: SUCCESS,
            },
        ),
        (
            {
                always_success_with_nested_mixed_unsuccessful_deps,
                no_deps_always_succeed_rule,
                always_success_with_unsuccessful_deps,
                no_deps_always_fail_rule,
            },
            {
                no_deps_always_succeed_rule: SUCCESS,
                no_deps_always_fail_rule: FAIL_TYPE1,
            },
        ),
    ],
    ids=[
        "single_success",
        "single_failure",
        "success_and_failure",
        "dependencies_met",
        "dependencies_not_met",
        "some_dependencies_not_met",
        "nested_dependencies_met",
        "nested_dependencies_not_met",
        "multiple_and_nested_dependencies_met_with_failures",
        "multiple_and_nested_dependencies_not_met",
    ],
)
def test_execute_rules_without_fields(rules, result):
    assert execute_rules(rules, {}) == result


@pytest.mark.parametrize(
    ("rules"),
    [
        {always_success_with_nested_mixed_unsuccessful_deps},
        {
            always_success_with_nested_mixed_unsuccessful_deps,
            no_deps_always_succeed_rule,
            no_deps_always_fail_rule,
        },
        {always_success_with_successful_deps, always_success_with_unsuccessful_deps},
    ],
    ids=["missing_all_deps", "missing_some_deps", "multiple_rules_with_missing_deps"],
)
def test_rules_with_missing_dependencies_are_invalid(rules):
    with pytest.raises(InvalidRuleError) as excinfo:
        execute_rules(
            rules,
            {},
        )
    assert "Invalid rules found" in str(excinfo.value)


def test_with_expected_fields_success():
    assert execute_rules(
        {has_expected_fields_rule},
        {"expected_fields": "foo"},
    ) == {has_expected_fields_rule: SUCCESS}


def test_with_expected_fields_failure():
    assert execute_rules(
        {has_expected_fields_rule},
        {"not_expected_fields": "foo"},
    ) == {has_expected_fields_rule: FAIL_TYPE1}
