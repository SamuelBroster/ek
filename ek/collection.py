from collections.abc import Callable
from typing import Generic, TypeVar

from ek.model import EntityModel

T = TypeVar("T", bound=EntityModel)
MigrationFunc = Callable[[EntityModel], T]


class EntityCollection(Generic[T]):
    # TODO: add a _type field on creation
    def __init__(self, model: type[T]) -> None:
        self.model = model
        self._migrations: dict[str, MigrationFunc[T]] = {}

    def register_migration(self, migration: MigrationFunc[T]) -> None:
        self._migrations[self.model.__class__.__name__] = migration
        raise NotImplementedError("TODO: implement migrations")

    def get(self, **kwargs) -> T:
        return self.model(**kwargs)
