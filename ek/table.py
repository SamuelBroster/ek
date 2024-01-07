import logging
from collections.abc import Sequence
from typing import TypeVar

from mypy_boto3_dynamodb import ServiceResource
from mypy_boto3_dynamodb.type_defs import AttributeDefinitionTypeDef

from ek.aws.type_mapping import DdbKeyType, python_type_to_ddb_key_type
from ek.entity_client.base import EntityClientBase, MigrationFunc
from ek.keys import PK, SK
from ek.model import EntityModel, get_model_name
from ek.rules.executor import execute_rules
from ek.rules.rules import RULES

_LOG = logging.getLogger(__name__)

T = TypeVar("T", bound=EntityModel)
U = TypeVar("U", bound=EntityModel)
V = TypeVar("V", bound=EntityClientBase)


class Table:
    # TODO: Figure out best way to initialise this
    # TODO: Allow specifying an EntityCollectionSync as a type so we can test without a real table
    def __init__(
        self, dynamodb: ServiceResource, table_name: str, client: type[EntityClientBase]
    ) -> None:
        self._dynamodb = dynamodb
        self._table_name = table_name

        self._table = dynamodb.Table(table_name)
        self._client = client
        self._entity_clients: dict[str, EntityClientBase] = {}

    def create_table(self) -> None:
        if len(self._entity_clients) == 0:
            raise ValueError("No models registered")

        # TODO: indexes
        response = self._dynamodb.create_table(
            TableName=self._table_name,
            AttributeDefinitions=attribute_definition(
                self.primary_key_type(), self.sort_key_type()
            ),
            KeySchema=[
                {"AttributeName": PK, "KeyType": "HASH"},
                {"AttributeName": SK, "KeyType": "RANGE"},
            ],
            BillingMode="PAY_PER_REQUEST",  # TODO: Expose this as an option and anything else?
        )
        _LOG.debug("Created table %s: %s", self._table_name, response)

    def delete_table(self) -> None:
        response = self._table.delete()
        _LOG.debug("Deleted table %s: %s", self._table_name, response)

    def register_migration(
        self, old_model: type[U], model: type[T], migration: MigrationFunc[U, T]
    ) -> None:
        collection = self._entity_clients[get_model_name(model)]
        collection.register_migration(old_model, migration)

    def register_model(self, model: type[T]) -> EntityClientBase[T]:
        model_name = get_model_name(model)
        if entity_client := self._entity_clients.get(model_name):
            if entity_client.model != model:
                raise KeyError(
                    f"Model {model_name} already registered with a different entity"
                )
            return entity_client

        self._validate_model(model)
        new_entity_client = self._client(model, self._table)
        self._entity_clients[model_name] = new_entity_client
        self._validate_models_are_consistent()

        return new_entity_client

    def primary_key_type(self):
        _LOG.debug("primary_key_type: %s", self._entity_clients)
        key_types = {
            client.model.model_fields[PK].annotation
            for client in self._entity_clients.values()
        }
        if len(key_types) == 0:
            raise ValueError("No primary key type")
        if len(key_types) > 1:
            raise ValueError(f"Multiple primary key types: {key_types}")

        key_type = key_types.pop()
        try:
            return python_type_to_ddb_key_type(key_type)
        except KeyError:
            raise ValueError(f"Unsupported primary key type: {key_type}") from None

    def sort_key_type(self):
        clients_with_sk = [
            client
            for client in self._entity_clients.values()
            if SK in client.model.model_fields
        ]
        if len(clients_with_sk) != 0 and len(clients_with_sk) != len(
            self._entity_clients
        ):
            raise ValueError("Some models have a sort key and some do not")
        if len(clients_with_sk) == 0:
            return None

        key_types = {
            client.model.model_fields[SK].annotation
            for client in self._entity_clients.values()
        }
        if len(key_types) > 1:
            raise ValueError(f"Multiple sort key types: {key_types}")

        key_type = key_types.pop()
        try:
            return python_type_to_ddb_key_type(key_type)
        except KeyError:
            raise ValueError(f"Unsupported sort key type: {key_type}") from None

    def _validate_model(self, model: type[EntityModel]) -> None:
        results = execute_rules(RULES, model.model_fields)
        if failures := [result for result in results.values() if not result.success]:
            message = "\n".join([result.message or "" for result in failures])
            raise ValueError(f"Validation errors:\n{message}")

    def _validate_models_are_consistent(self):
        # Rely on the fact that we only allow one primary key type and one sort key type
        self.primary_key_type()
        self.sort_key_type()


def attribute_definition(
    pk_type: DdbKeyType, sk_type: DdbKeyType | None
) -> Sequence[AttributeDefinitionTypeDef]:
    attribute_definition: list[AttributeDefinitionTypeDef] = [
        {
            "AttributeName": PK,
            "AttributeType": pk_type,
        }
    ]
    if sk_type:
        attribute_definition.append(
            {
                "AttributeName": SK,
                "AttributeType": sk_type,
            }
        )
    return attribute_definition
