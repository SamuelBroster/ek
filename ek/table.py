from typing import TypeVar

from mypy_boto3_dynamodb import ServiceResource

from ek.collection import EntityCollectionSync, MigrationFunc
from ek.model import EntityModel, get_model_name

T = TypeVar("T", bound=EntityModel)


class Table:
    # TODO: Figure out best way to initialise this
    def __init__(self, dynamodb: ServiceResource, table_name: str) -> None:
        self._table = dynamodb.Table(table_name)
        self._collections: dict[str, EntityCollectionSync] = {}

    def register_migration(
        self, old_model: type[EntityModel], model: type[T], migration: MigrationFunc[T]
    ) -> None:
        collection = self._collections[get_model_name(model)]
        collection.register_migration(old_model, migration)

    def register_model(self, model: type[T]) -> EntityCollectionSync[T]:
        model_name = get_model_name(model)
        if collection := self._collections.get(model_name):
            if collection.model != model:
                raise KeyError(
                    f"Model {model_name} already registered with a different entity"
                )
            return collection

        self._validate_model(model)
        new_collection: EntityCollectionSync = EntityCollectionSync(model, self._table)
        self._collections[model_name] = new_collection
        return new_collection

    def _validate_model(self, model: type[T]) -> None:
        # TODO: validate model has a 'pk' field that is a string
        # TODO: validate that if there is an 'sk' field it is a string
        # TODO: validate that template fields are in the model
        # TODO: police the Pydantic fields that we allow
        pass
