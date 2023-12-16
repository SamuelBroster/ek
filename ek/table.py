from typing import TypeVar

from ek.collection import EntityCollection, MigrationFunc
from ek.model import EntityModel, get_model_name

T = TypeVar("T", bound=EntityModel)


class Table:
    def __init__(self) -> None:
        self.collections: dict[str, EntityCollection] = {}

    def register_migration(self, model: type[T], migration: MigrationFunc[T]) -> None:
        collection = self.collections[get_model_name(model)]
        collection.register_migration(migration)

    def register_model(self, model: type[T]) -> EntityCollection[T]:
        model_name = get_model_name(model)
        if collection := self.collections.get(model_name):
            if collection.model != model:
                raise KeyError(
                    f"Model {model_name} already registered with a different entity"
                )
            return collection

        self._validate_model(model)
        new_collection: EntityCollection = EntityCollection(model)
        self.collections[model_name] = new_collection
        return new_collection

    def _validate_model(self, model: type[T]) -> None:
        # TODO: validate model has a 'pk' field that is a string
        # TODO: validate that if there is an 'sk' field it is a string
        # TODO: validate that template fields are in the model
        # TODO: police the Pydantic fields that we allow
        pass
