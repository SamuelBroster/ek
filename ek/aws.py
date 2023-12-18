from dataclasses import dataclass
from enum import Enum
from typing import Any, Generic, TypeVar

from ek.model import EntityModel

E = TypeVar("E", bound=EntityModel)


class ConsumedCapacity(Enum):
    INDEXES = "INDEXES"
    TOTAL = "TOTAL"
    NONE = "NONE"

class ReturnValues(Enum):
    NONE = "NONE"
    ALL_OLD = "ALL_OLD"
    UPDATED_OLD = "UPDATED_OLD"
    ALL_NEW = "ALL_NEW"
    UPDATED_NEW = "UPDATED_NEW"

class ItemCollectionMetrics(Enum):
    NONE = "NONE"
    SIZE = "SIZE"

class ReturnValuesOnConditionCheckFailure(Enum):
    NONE = "NONE"
    ALL_OLD = "ALL_OLD"

ExpressionAttributeNames = dict[str, str]
ExpressionAttributeValues = dict[str, Any]

@dataclass
class GetItemResponse(Generic[E]):
    item: E | None
    consumed_capacity: dict[str, Any] | None
