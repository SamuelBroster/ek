import boto3

# TODO: aioboto3 ?

dynamodb = boto3.resource(
    "dynamodb",
    endpoint_url="http://localhost:8000",
    aws_access_key_id="ACCESSID",
    aws_secret_access_key="ACCESS`KEY",
)

TABLE = "MyTable"


def test_dynamodb_fixture(session_scoped_container_getter):
    try:
        dynamodb.create_table(
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

    table = dynamodb.Table(TABLE)
    response = table.get_item(
        Key={"pk": "someval"},
    )
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
