from decimal import Decimal

import pytest

from ek.entity_client.conditions import verify_sort_key_condition


@pytest.mark.parametrize(
    ("condition", "message"),
    [
        (dict(between=(1, "1")), "Between condition must have values of same type"),
        (dict(between=(1, b"1")), "Between condition must have values of same type"),
        (dict(between=("1", 1)), "Between condition must have values of same type"),
        (dict(between=("1", b"sd")), "Between condition must have values of same type"),
        (dict(between=(b"1", 1)), "Between condition must have values of same type"),
        (dict(between=(b"1", "1")), "Between condition must have values of same type"),
        (dict(begins=1, begins_with=2), "Max one condition allowed"),
        (dict(between=(2, 1)), "Between condition must have values in ascending order"),
        (
            dict(between=("2", "1")),
            "Between condition must have values in ascending order",
        ),
        (
            dict(between=(b"2", b"1")),
            "Between condition must have values in ascending order",
        ),
        (dict(invalid=3), "Invalid condition"),
    ],
)
def test_sort_key_condition_verification_failures(condition, message):
    with pytest.raises(ValueError, match=message):
        verify_sort_key_condition(condition)


@pytest.mark.parametrize(
    ("condition"),
    [
        (dict()),
        (dict(between=(1, 3))),
        (dict(between=(1, Decimal("1.2")))),
        (dict(begins=1)),
        (dict(begins_with=1)),
        ({"<": 1}),
        ({"<=": 1}),
        ({"==": 1}),
        ({">=": 1}),
        ({">": 1}),
    ],
)
def test_sort_key_condition_verification_succeeds(condition):
    verify_sort_key_condition(condition)
