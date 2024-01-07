from collections.abc import Mapping, Sequence
from decimal import Decimal
from typing import Any, Literal

AllowedPythonKeyType = str | int | Decimal | bytes | bytearray
AllowedPythonType = (
    bytes
    | bytearray
    | str
    | int
    | Decimal
    | bool
    | set[int]
    | set[Decimal]
    | set[str]
    | set[bytes]
    | set[bytearray]
    | Sequence[Any]
    | Mapping[str, Any]
    | None
)
DdbMapping = Mapping[str, AllowedPythonType]

DdbKeyType = Literal["B", "N", "S"]
DdbType = Literal["B", "BS", "BOOL", "L", "M", "N", "NS", "NULL", "S", "SS"]


GENERAL_MAPPING: dict[type[AllowedPythonType], DdbType] = {
    bytes: "B",
    bytearray: "B",
    str: "S",
    int: "N",
    Decimal: "N",
    bool: "BOOL",
    set[int]: "NS",
    set[Decimal]: "NS",
    set[str]: "SS",
    set[bytes]: "BS",
    set[bytearray]: "BS",
    Sequence[Any]: "L",
    Mapping[str, Any]: "M",
}

KEY_MAPPING: dict[type[AllowedPythonKeyType], DdbKeyType] = {
    bytes: "B",
    bytearray: "B",
    str: "S",
    int: "N",
    Decimal: "N",
}


def python_type_to_ddb_type(python_type: type[AllowedPythonType]) -> DdbType:
    return GENERAL_MAPPING[python_type]


def python_type_to_ddb_key_type(python_type: type[AllowedPythonKeyType]) -> DdbKeyType:
    return KEY_MAPPING[python_type]
