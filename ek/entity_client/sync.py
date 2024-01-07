import logging

from ek.entity_client.base import (
    PUT_ITEM_OPTIONS_DEFAULTS,
    EntityClientBase,
    T,
)
from ek.entity_client.options import (
    GET_ITEM_OPTION_DEFAULTS,
    GetItemOptions,
    PutItemOptions,
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
        _options: GetItemOptions = GET_ITEM_OPTION_DEFAULTS,
        **kwargs,
    ) -> GetItemResponse[T]:
        options: GetItemOptions = dict(**GET_ITEM_OPTION_DEFAULTS, **_options)
        # TODO: Add support for projection expressions. We should allow the user to specify
        # a list of fields to return but will need to figure out how to do partial vaildation
        # with pydantic.

        key = self.primary_key(**kwargs)
        _LOG.info("Get item from %s: %s (%s)", self._table.name, key, options)
        response = self._table.get_item(
            Key=key,
            ConsistentRead=options["consistent_read"],
            ReturnConsumedCapacity=options["return_consumed_capacity"].value,
        )
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
        _options: PutItemOptions = PUT_ITEM_OPTIONS_DEFAULTS,
    ):
        options: PutItemOptions = dict(**PUT_ITEM_OPTIONS_DEFAULTS, **_options)
        # TODO: Add support for return_values, consumed capacfity and return values on condition check failure
        _LOG.info("Put item to %s: %s", self._table.name, item.model_dump_ddb())
        response = self._table.put_item(
            Item=item.model_dump_ddb(),
            ReturnValues=options["return_values"].value,
            ReturnConsumedCapacity=options["return_consumed_capacity"].value,
            ReturnValuesOnConditionCheckFailure=options[
                "return_values_on_condition_check_failure"
            ].value,
        )
        _LOG.info("Put item response: %s", response)

        # TODO: the return type is dependent on the return_values parameter
        return PutItemResponse(
            item=response.get("Item"),
            consumed_capacity=ConsumedCapacityResponse.from_ddb(
                response.get("ConsumedCapacity")
            ),
        )
