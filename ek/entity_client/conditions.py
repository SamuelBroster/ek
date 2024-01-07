from typing import Literal, NotRequired, TypedDict

from ek.aws.type_mapping import AllowedPythonKeyType, python_type_to_ddb_type

ALLOWED_CONDITIONS = {"begins", "begins_with", "between", "<", "<=", "==", ">", ">="}
Operator = Literal["==", "<", "<=", ">", ">=", "begins_with", "between", "begins"]

SortKeyCondition = TypedDict(
    "SortKeyCondition",
    {
        "begins": NotRequired[AllowedPythonKeyType],
        "begins_with": NotRequired[AllowedPythonKeyType],
        "between": NotRequired[tuple[AllowedPythonKeyType, AllowedPythonKeyType]],
        "<": NotRequired[AllowedPythonKeyType],
        "<=": NotRequired[AllowedPythonKeyType],
        "==": NotRequired[AllowedPythonKeyType],
        ">": NotRequired[AllowedPythonKeyType],
        ">=": NotRequired[AllowedPythonKeyType],
    },
)

DEFAULT_SORT_KEY_CONDITION: SortKeyCondition = {}


def verify_sort_key_condition(condition: SortKeyCondition) -> None:
    if len(condition) > 1:
        raise ValueError(f"Max one condition allowed: {condition}")

    if between := condition.get("between"):
        if len(between) != 2:
            raise ValueError(f"Between condition must have two values: {between}")
        elif python_type_to_ddb_type(type(between[0])) != python_type_to_ddb_type(
            type(between[1])
        ):
            raise ValueError(
                f"Between condition must have values of same type: {between}"
            )
        elif between[0] > between[1]:  # type: ignore [operator]
            raise ValueError(
                f"Between condition must have values in ascending order: {between}"
            )

    for key in condition:
        if key not in ALLOWED_CONDITIONS:
            raise ValueError(f"Invalid condition: {condition}")
