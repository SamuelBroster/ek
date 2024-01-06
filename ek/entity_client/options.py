from dataclasses import dataclass
from enum import Enum
from typing import Any


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
class GetItemOptions:
    consistent_read: bool = False
    return_consumed_capacity: ConsumedCapacity = ConsumedCapacity.NONE


@dataclass
class PutItemOptions:
    return_values: ReturnValues = ReturnValues.NONE
    return_consumed_capacity: ConsumedCapacity = ConsumedCapacity.NONE
    return_values_on_condition_check_failure: ReturnValuesOnConditionCheckFailure = (
        ReturnValuesOnConditionCheckFailure.NONE
    )
