import pytest

from ek.entity_client.local import EntityClientLocal
from ek.model import EntityModel


@pytest.fixture()
def simple_model():
    class SimpleModel(EntityModel):
        pk: str = "CU#{company_id}"
        sk: str = "US#{user_id}"
        company_id: str
        user_id: str

    return SimpleModel


@pytest.fixture()
def simple_client(simple_model, dummy_dynamodb_resource):
    return EntityClientLocal(simple_model, dummy_dynamodb_resource.Table("TestTable"))


def test_put_and_get(simple_client, simple_model):
    user = simple_model(company_id="COMP-123", user_id="USR-123")
    simple_client.put_item(user)
    response = simple_client.get_item(company_id="COMP-123", user_id="USR-123")
    assert response.item == user


def test_query(simple_client, simple_model):
    user1 = simple_model(company_id="COMP-123", user_id="USR-123")
    user2 = simple_model(company_id="COMP-123", user_id="USR-456")
    user3 = simple_model(company_id="COMP-123", user_id="USR-490")
    user4 = simple_model(company_id="COMP-456", user_id="USR-789")
    for user in [user1, user2, user3, user4]:
        simple_client.put_item(user)

    response = simple_client.query(company_id="COMP-123")
    assert response.items == [user1, user2, user3]

    response = simple_client.query(company_id="COMP-123", sk={"begins": "US#-4"})
    assert response.items == [user2, user3]

    response = simple_client.query(company_id="COMP-123", sk={">": "US#-46"})
    assert response.items == [user3]
