from typing import TypeVar

from ek.collection import EntityCollection, MigrationFunc
from ek.model import EntityModel

T = TypeVar("T", bound=EntityModel)


class Table:
    def __init__(self) -> None:
        self.collections: dict[type[EntityModel], EntityCollection] = {}

    def register_migration(self, model: type[T], migration: MigrationFunc[T]) -> None:
        collection = self.collections[model]
        collection.register_migration(migration)

    def register_model(self, model: type[T]) -> EntityCollection[T]:
        if model in self.collections:
            return self.collections[model]

        self._validate_model(model)
        collection: EntityCollection = EntityCollection(model)
        self.collections[model] = collection
        return collection

    def _validate_model(self, model: type[T]) -> None:
        # TODO: validate model has a 'pk' field that is a string
        # TODO: validate that if there is an 'sk' field it is a string
        # TODO: validate that template fields are in the model
        # TODO: police the Pydantic fields that we allow
        pass
