import pickle
import tempfile
from pathlib import Path

from mypy_boto3_dynamodb.service_resource import Table

from ek.entity_client.base import (
    DEFAULT_GET_ITEM_OPTIONS,
    DEFAULT_PUT_ITEM_OPTIONS,
    EntityClientBase,
    T,
)
from ek.entity_client.responses import GetItemResponse, PutItemResponse
from ek.keys import PK, SK

PrimaryKey = tuple[str, str | None]


class EntityClientLocal(EntityClientBase[T]):
    STORE_PATH = Path(tempfile.NamedTemporaryFile().name)

    def __init__(self, model: type[T], table: Table) -> None:
        super().__init__(model, table)

        self._init_store_path()
        self._data_store = self._load_data_store()

    def _init_store_path(self):
        if not self.STORE_PATH.exists():
            self._save_data_store({})

    def _save_data_store(self, data: dict[PrimaryKey, T]):
        with open(self.STORE_PATH, "wb") as f:
            pickle.dump(data, f)

    def _load_data_store(self) -> dict[PrimaryKey, T]:
        with open(self.STORE_PATH, "rb") as f:
            return pickle.load(f)

    def primary_key_tuple(self, **kwargs) -> PrimaryKey:
        primary_key = self.primary_key(**kwargs)
        return (primary_key[PK], primary_key.get(SK))

    def get_item(
        self,
        _options=DEFAULT_GET_ITEM_OPTIONS,
        **kwargs,
    ) -> GetItemResponse[T]:
        primary_key = self.primary_key_tuple(**kwargs)
        item = self._data_store.get(primary_key)
        return GetItemResponse(item=item)

    def put_item(
        self,
        item: T,
        _options=DEFAULT_PUT_ITEM_OPTIONS,
    ):
        primary_key = self.primary_key_tuple(**item.model_dump_ddb())
        self._data_store[primary_key] = item
        return PutItemResponse(
            item=item,
        )
