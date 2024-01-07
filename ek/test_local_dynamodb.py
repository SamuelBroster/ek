TABLE = "MyTable"


def test_dynamodb_fixture(dynamodb_resource):
    try:
        dynamodb_resource.create_table(
            TableName=TABLE,
            AttributeDefinitions=[
                {"AttributeName": "pk", "AttributeType": "S"},
            ],
            KeySchema=[
                {"AttributeName": "pk", "KeyType": "HASH"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
    except Exception:
        print("Table already exists")

    table = dynamodb_resource.Table(TABLE)
    response = table.get_item(
        Key={"pk": "someval"},
    )
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
