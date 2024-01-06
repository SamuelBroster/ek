from typing import TypeVar

from mypy_boto3_dynamodb import ServiceResource

from ek.entity_client.base import EntityClientBase, MigrationFunc
from ek.model import EntityModel, get_model_name

T = TypeVar("T", bound=EntityModel)
U = TypeVar("U", bound=EntityModel)
V = TypeVar("V", bound=EntityClientBase)


class Table:
    # TODO: Figure out best way to initialise this
    # TODO: Allow specifying an EntityCollectionSync as a type so we can test without a real table
    def __init__(
        self, dynamodb: ServiceResource, table_name: str, client: type[EntityClientBase]
    ) -> None:
        self._table = dynamodb.Table(table_name)
        self._client = client
        self._entity_clients: dict[str, EntityClientBase] = {}

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
        return new_entity_client

    def _validate_model(self, model: type[T]) -> None:
        # TODO: validate model has a 'pk' field that is a string
        # TODO: validate that if there is an 'sk' field it is a string
        # TODO: validate that template fields are in the model
        # TODO: police the Pydantic fields that we allow
        pass
