from enum import Enum
from typing import Any, NotRequired, TypedDict


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


class GetItemOptions(TypedDict):
    consistent_read: NotRequired[bool]
    return_consumed_capacity: NotRequired[ConsumedCapacity]


GET_ITEM_OPTION_DEFAULTS: GetItemOptions = dict(
    consistent_read=False, return_consumed_capacity=ConsumedCapacity.NONE
)


class PutItemOptions(TypedDict):
    return_values: NotRequired[ReturnValues]
    return_consumed_capacity: NotRequired[ConsumedCapacity]
    return_values_on_condition_check_failure: NotRequired[
        ReturnValuesOnConditionCheckFailure
    ]


PUT_ITEM_OPTIONS_DEFAULTS: PutItemOptions = dict(
    return_values=ReturnValues.NONE,
    return_consumed_capacity=ConsumedCapacity.NONE,
    return_values_on_condition_check_failure=ReturnValuesOnConditionCheckFailure.NONE,
)


class QueryOptions(TypedDict):
    pass


QUERY_OPTIONS_DEFAULTS: QueryOptions = dict()
