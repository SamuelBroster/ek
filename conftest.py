import boto3
import pytest

pytest_plugins = ["docker_compose"]

dynamodb_container_name = "dynamodb-local"


@pytest.fixture(scope="session")
def dynamodb_resource(session_scoped_container_getter):
    container = session_scoped_container_getter.get(dynamodb_container_name)
    network_info = container.network_info[0]
    return boto3.resource(
        "dynamodb",
        endpoint_url=f"http://{network_info.hostname}:{network_info.host_port}",
        aws_access_key_id="ACCESSID",
        aws_secret_access_key="ACCESSKEY",
    )
