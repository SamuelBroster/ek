import pytest

from ek.model import EntityModel
from ek.table import Table


@pytest.fixture()
def simple_model():
    class SimpleModel(EntityModel):
        pk: str = "CU#{customer_id}"
        customer_id: str

    return SimpleModel


@pytest.fixture()
def table(dynamodb_resource):
    return Table(dynamodb_resource, "OneTable")


def test_register_a_simple_model(table, simple_model):
    model_collection = table.register_model(simple_model)
    model = model_collection.get(customer_id="123")
    assert model == simple_model(pk="CU#123", customer_id="123")


def test_register_a_simple_model_twice(table, simple_model):
    table.register_model(simple_model)
    model_collection = table.register_model(simple_model)
    model = model_collection.get(customer_id="123")
    assert model == simple_model(pk="CU#123", customer_id="123")


def test_cant_register_different_classes_under_the_same_name(table, simple_model):
    class SimpleModel(EntityModel):
        pk: str = "CU#{customer_id}"
        customer_id: str

    table.register_model(simple_model)
    with pytest.raises(KeyError):
        table.register_model(SimpleModel)
