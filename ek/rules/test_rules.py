from decimal import Decimal

import pytest

from ek.entity_client.local import EntityClientLocal
from ek.model import EntityModel
from ek.table import Table


@pytest.fixture()
def table(dummy_dynamodb_resource):
    return Table(dummy_dynamodb_resource, "OneTable", EntityClientLocal)


class InvalidPkType(EntityModel):
    pk: float


class MissingPkType(EntityModel):
    pass


class InvalidSkType(EntityModel):
    pk: str
    sk: list[str]


@pytest.mark.parametrize(
    ("model", "error_message"),
    [
        (MissingPkType, "missing pk attribute"),
        (InvalidPkType, "pk attribute type <class 'float'> is not in"),
        (InvalidSkType, "sk attribute type list\[str\] is not in"),
    ],
)
def test_table_rejects_invalid_models(table, model, error_message):
    with pytest.raises(ValueError, match=error_message):
        table.register_model(model)


class JustPkStr(EntityModel):
    pk: str


class JustPkInt(EntityModel):
    pk: int


class JustPkDecimal(EntityModel):
    pk: Decimal


class JustPkBytes(EntityModel):
    pk: bytes


class PkAndSkStr(EntityModel):
    pk: int
    sk: str


class PkAndSkInt(EntityModel):
    pk: Decimal
    sk: int


class PkAndSkDecimal(EntityModel):
    pk: str
    sk: Decimal


class PkAndSkBytes(EntityModel):
    pk: bytes
    sk: bytes


# TODO: Remove support for bytearray
# class JustPkBytesArray(EntityModel):
#     pk: bytearray


@pytest.mark.parametrize(
    ("model"),
    [
        (JustPkStr),
        (JustPkInt),
        (JustPkDecimal),
        (JustPkBytes),
        (PkAndSkStr),
        (PkAndSkInt),
        (PkAndSkDecimal),
        (PkAndSkBytes),
    ],
)
def test_table_accepts_valid_models(table, model):
    table.register_model(model)
