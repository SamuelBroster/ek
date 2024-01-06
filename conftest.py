import boto3
import pytest

pytest_plugins = ["docker_compose"]

dynamodb_container_name = "dynamodb-local"


def resource(host: str, port: str):
    return boto3.resource(
        "dynamodb",
        endpoint_url=f"http://{host}:{port}",
        aws_access_key_id="ACCESSID",
        aws_secret_access_key="ACCESSKEY",
    )


@pytest.fixture(scope="session")
def dynamodb_resource(session_scoped_container_getter):
    # TODO: cleanup table after / between tests
    container = session_scoped_container_getter.get(dynamodb_container_name)
    network_info = container.network_info[0]
    return resource(network_info.hostname, network_info.host_port)


@pytest.fixture(scope="session")
def dummy_dynamodb_resource():
    return resource("localhost", "8000")
