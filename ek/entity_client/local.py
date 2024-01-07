import operator
import pickle
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import TypeVar

from mypy_boto3_dynamodb.service_resource import Table

from ek.aws.type_mapping import AllowedPythonKeyType
from ek.entity_client.base import (
    EntityClientBase,
    T,
)
from ek.entity_client.conditions import (
    DEFAULT_SORT_KEY_CONDITION,
    verify_sort_key_condition,
)
from ek.entity_client.options import (
    GET_ITEM_OPTION_DEFAULTS,
    PUT_ITEM_OPTIONS_DEFAULTS,
    QUERY_OPTIONS_DEFAULTS,
)
from ek.entity_client.responses import GetItemResponse, PutItemResponse, QueryResponse
from ek.keys import PK, SK

S = TypeVar("S")

PrimaryKey = tuple[AllowedPythonKeyType, AllowedPythonKeyType | None]
Store = dict[AllowedPythonKeyType, dict[AllowedPythonKeyType | None, S]]


class EntityClientLocal(EntityClientBase[T]):
    STORE_PATH = Path(tempfile.NamedTemporaryFile().name)

    def __init__(self, model: type[T], table: Table) -> None:
        super().__init__(model, table)

        self._init_store_path()
        self._data_store = self._load_data_store()

    def _init_store_path(self):
        if not self.STORE_PATH.exists():
            self._save_data_store(defaultdict(dict))

    def _save_data_store(self, data: Store[T]):
        with open(self.STORE_PATH, "wb") as f:
            pickle.dump(data, f)

    def _load_data_store(self) -> Store[T]:
        with open(self.STORE_PATH, "rb") as f:
            return pickle.load(f)

    def primary_key_tuple(self, **kwargs) -> PrimaryKey:
        primary_key = self.primary_key(**kwargs)
        return (primary_key[PK], primary_key.get(SK))

    def get_item(
        self,
        _options=GET_ITEM_OPTION_DEFAULTS,
        **kwargs,
    ) -> GetItemResponse[T]:
        pk, sk = self.primary_key_tuple(**kwargs)
        item = self._data_store.get(pk, {}).get(sk)
        return GetItemResponse(item=item)

    def put_item(
        self,
        item: T,
        _options=PUT_ITEM_OPTIONS_DEFAULTS,
    ):
        pk, sk = self.primary_key_tuple(**item.model_dump_ddb())
        self._data_store[pk][sk] = item
        return PutItemResponse(
            item=item,
        )

    def query(
        self,
        sk=DEFAULT_SORT_KEY_CONDITION,
        _options=QUERY_OPTIONS_DEFAULTS,
        **kwargs,
    ):
        verify_sort_key_condition(sk)

        pk, sk = self.primary_key_tuple(**kwargs)
        pk_dict = self._data_store.get(pk, {})
        if not sk:
            items = list(pk_dict)
        else:
            assert len(sk) == 1
            condition, value = sk.keys()[0], sk.values()[0]
            if condition == "begins_with" or condition == "begins":
                items = [item for sk, item in pk_dict.items() if sk.startswith(value)]
            elif condition == "between":
                items = [
                    item
                    for sk, item in pk_dict.items()
                    if condition[0] <= sk <= condition[1]
                ]
            else:
                cmp = {
                    "==": operator.eq,
                    "<": operator.lt,
                    "<=": operator.le,
                    ">": operator.gt,
                    ">=": operator.ge,
                }[condition]
                items = [item for sk, item in pk_dict.items() if cmp(sk, value)]

        return QueryResponse(items=items)
