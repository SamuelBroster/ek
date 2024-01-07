import pytest

from ek.entity_client.sync import EntityClientSync
from ek.model import EntityModel
from ek.table import Table


@pytest.fixture()
def simple_model():
    class SimpleModel(EntityModel):
        pk: str = "CU#{customer_id}"
        sk: str = "EMPTY"
        customer_id: str

    return SimpleModel


@pytest.fixture()
def simple_model_instance(simple_model):
    return simple_model(customer_id="abc-123")


@pytest.fixture()
def simple_model_client(simple_model, dynamodb_resource):
    table = Table(dynamodb_resource, "TestTable", EntityClientSync)
    model = table.register_model(simple_model)

    table.create_table()
    try:
        yield model
    finally:
        table.delete_table()


def test_put_and_get_item(simple_model_client, simple_model_instance):
    simple_model_client.put_item(simple_model_instance)
    response = simple_model_client.get_item(
        customer_id=simple_model_instance.customer_id
    )
    assert response.item == simple_model_instance


# TODO: Test when there are missing parameters
# TODO: Test attempting to put the wrong entity

# TODO: Test nesteded fields and dictionaries (here or elsewhere?)
