from decimal import Decimal

from ek.keys import PK, SK
from ek.rules.executor import ModelFields, ModelRule
from ek.rules.results import SUCCESS, Result, failure


def has_pk_check(fields: ModelFields) -> Result:
    if PK not in fields:
        return failure("missing pk attribute")
    return SUCCESS


def pk_has_valid_type_check(fields: ModelFields) -> Result:
    valid_types = {str, int, Decimal, bytes, bytearray}
    pk = fields[PK]
    if pk.annotation not in valid_types:
        valid_types_str = ", ".join([str(t) for t in valid_types])
        return failure(
            f"{PK} attribute type {pk.annotation} is not in {valid_types_str}"
        )
    return SUCCESS


def sk_has_valid_type_check(fields: ModelFields) -> Result:
    valid_types = {str, int, Decimal, bytes, bytearray}
    sk = fields.get(SK)
    if sk and sk.annotation not in valid_types:
        valid_types_str = ", ".join([str(t) for t in valid_types])
        return failure(
            f"{SK} attribute type {sk.annotation} is not in {valid_types_str}"
        )
    return SUCCESS


has_pk = ModelRule(check=has_pk_check, dependencies=frozenset())
pk_has_valid_type = ModelRule(
    check=pk_has_valid_type_check, dependencies=frozenset({has_pk})
)
sk_has_valid_type = ModelRule(check=sk_has_valid_type_check, dependencies=frozenset({}))

RULES: set[ModelRule] = {has_pk, pk_has_valid_type, sk_has_valid_type}

# TODO: validate that template fields are in the model
# TODO: police the Pydantic fields that we allow
# TODO: all registered entities must have the same type of PK
# TODO: allow mix of optional SK and required SK by defaulting SKs with a dummy value?
