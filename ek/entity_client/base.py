from abc import ABC, abstractmethod
from collections import UserDict
from collections.abc import Callable
from typing import Any, Generic, TypeVar

from mypy_boto3_dynamodb.service_resource import Table

from ek.entity_client.conditions import DEFAULT_SORT_KEY_CONDITION, SortKeyCondition
from ek.entity_client.options import (
    GET_ITEM_OPTION_DEFAULTS,
    PUT_ITEM_OPTIONS_DEFAULTS,
    QUERY_OPTIONS_DEFAULTS,
    GetItemOptions,
    PutItemOptions,
    QueryOptions,
)
from ek.entity_client.responses import GetItemResponse, PutItemResponse
from ek.model import EntityModel

T = TypeVar("T", bound=EntityModel)
U = TypeVar("U", bound=EntityModel)
MigrationFunc = Callable[[U], T]


class MigrationDict(UserDict[type[EntityModel], MigrationFunc[Any, T]]):
    def __setitem__(self, key: type[U], value: MigrationFunc[U, T]) -> None:
        return super().__setitem__(key, value)

    def __getitem__(self, key: type[U]) -> MigrationFunc[U, T]:
        return super().__getitem__(key)


class EntityClientBase(Generic[T], ABC):
    def __init__(self, model: type[T], table: Table) -> None:
        self.model = model
        self._table = table
        self._migrations: MigrationDict[T] = MigrationDict()

    def primary_key(self, **kwargs) -> dict[str, str]:
        return self.model.primary_key(**kwargs)

    def register_migration(
        self, old_model: type[U], migration: MigrationFunc[U, T]
    ) -> None:
        self._migrations[old_model] = migration
        raise NotImplementedError("TODO: implement migrations")

    @abstractmethod
    def get_item(
        self, _options: GetItemOptions = GET_ITEM_OPTION_DEFAULTS, **kwargs
    ) -> GetItemResponse[T]:
        pass

    @abstractmethod
    def put_item(
        self,
        item: T,
        _options: PutItemOptions = PUT_ITEM_OPTIONS_DEFAULTS,
    ) -> PutItemResponse[T]:
        pass

    @abstractmethod
    def query(
        self,
        sk: SortKeyCondition = DEFAULT_SORT_KEY_CONDITION,
        _options: QueryOptions = QUERY_OPTIONS_DEFAULTS,
        **kwargs,
    ):
        pass
