import pytest

from ek.entity_client.local import EntityClientLocal
from ek.model import EntityModel
from ek.table import Table


@pytest.fixture()
def simple_model():
    class SimpleModel(EntityModel):
        pk: str = "CU#{customer_id}"
        customer_id: str

    return SimpleModel


@pytest.fixture()
def simple_model_instance(simple_model):
    return simple_model(customer_id="abc-123")


@pytest.fixture()
def table(dummy_dynamodb_resource):
    return Table(dummy_dynamodb_resource, "OneTable", EntityClientLocal)


def test_register_a_simple_model(table, simple_model, simple_model_instance):
    models_client = table.register_model(simple_model)
    models_client.put_item(simple_model_instance)
    response = models_client.get_item(customer_id=simple_model_instance.customer_id)
    assert response.item == simple_model_instance


def test_register_a_simple_model_twice(table, simple_model, simple_model_instance):
    models_client1 = table.register_model(simple_model)
    models_client1.put_item(simple_model_instance)

    models_client2 = table.register_model(simple_model)
    response = models_client2.get_item(customer_id=simple_model_instance.customer_id)
    assert response.item == simple_model_instance


def test_cant_register_different_classes_under_the_same_name(table, simple_model):
    class SimpleModel(EntityModel):
        pk: str = "CU#{customer_id}"
        customer_id: str

    table.register_model(simple_model)
    with pytest.raises(KeyError):
        table.register_model(SimpleModel)
