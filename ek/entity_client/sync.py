import logging

from ek.entity_client.base import (
    DEFAULT_GET_ITEM_OPTIONS,
    DEFAULT_PUT_ITEM_OPTIONS,
    EntityClientBase,
    T,
)
from ek.entity_client.responses import (
    ConsumedCapacityResponse,
    GetItemResponse,
    PutItemResponse,
)

_LOG = logging.getLogger(__name__)


class EntityClientSync(EntityClientBase[T]):
    # TODO: add a _type field on creation
    def get_item(
        self,
        _options=DEFAULT_GET_ITEM_OPTIONS,
        **kwargs,
    ) -> GetItemResponse[T]:
        aws_args = dict(
            Key=self.primary_key(**kwargs),
            ConsistentRead=_options.consistent_read,
            ReturnConsumedCapacity=_options.return_consumed_capacity.value,
        )
        # TODO: Add support for projection expressions. We should allow the user to specify
        # a list of fields to return but will need to figure out how to do partial vaildation
        # with pydantic.

        _LOG.info("Get item from %s: %s", self._table.name, aws_args)
        response = self._table.get_item(**aws_args)
        _LOG.info("Get item response: %s", response)

        item = None
        if item_dict := response.get("Item"):
            item = self.model(**item_dict)
        consumed_capacity = ConsumedCapacityResponse.from_ddb(
            response.get("ConsumedCapacity")
        )

        return GetItemResponse(item=item, consumed_capacity=consumed_capacity)

    def put_item(
        self,
        item: T,
        _options=DEFAULT_PUT_ITEM_OPTIONS,
    ):
        # TODO: Add support for return_values, consumed capacfity and return values on condition check failure
        _LOG.info("Put item to %s: %s", self._table.name, item.model_dump_ddb())
        response = self._table.put_item(
            Item=item.model_dump_ddb(),
            ReturnValues=_options.return_values.value,
            ReturnConsumedCapacity=_options.return_consumed_capacity.value,
            ReturnValuesOnConditionCheckFailure=_options.return_values_on_condition_check_failure.value,
        )
        _LOG.info("Put item response: %s", response)

        # TODO: the return type is dependent on the return_values parameter
        return PutItemResponse(
            item=response.get("Item"),
            consumed_capacity=ConsumedCapacityResponse.from_ddb(
                response.get("ConsumedCapacity")
            ),
        )
