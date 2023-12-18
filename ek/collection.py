from collections.abc import Callable
from typing import Generic, TypeVar

from mypy_boto3_dynamodb.service_resource import Table

from ek.aws import ConsumedCapacity, ExpressionAttributeNames, GetItemResponse, ReturnValues
from ek.model import EntityModel

T = TypeVar("T", bound=EntityModel)
MigrationFunc = Callable[[EntityModel], T]


class EntityCollectionBase(Generic[T]):
    def __init__(self, model: type[T], table: Table) -> None:
        self.model = model
<<<<<<< Updated upstream
        self._migrations: dict[str, MigrationFunc[T]] = {}
=======
        self._table = table
        self._migrations: MigrationDict[T] = MigrationDict()
>>>>>>> Stashed changes

    def register_migration(
        self, old_model: type[EntityModel], migration: MigrationFunc[T]
    ) -> None:
        self._migrations[old_model.__class__.__name__] = migration
        raise NotImplementedError("TODO: implement migrations")


class EntityCollectionSync(EntityCollectionBase[T]):
    # TODO: add a _type field on creation
    def get_item(
        self,
        *,
        consistent_read=False,
        return_consumed_capacity: ConsumedCapacity = ConsumedCapacity.NONE,
        projection_expression: str | None = None,
        expression_attribute_names: ExpressionAttributeNames | None = None, # TODO: this shouldn't be needed?
        **kwargs,
    ) -> GetItemResponse[T]:
        aws_args = dict(
            Key=self.model.primary_key(**kwargs),
            ConsistentRead=consistent_read,
            ReturnConsumedCapacity=return_consumed_capacity.value,
            ExpressionAttributeNames=expression_attribute_names,         )
        if projection_expression:
            aws_args["ProjectionExpression"] = projection_expression

        response = self._table.get_item(**aws_args)
        return GetItemResponse(
            item=response.get("Item"),
            consumed_capacity=response.get("ConsumedCapacity"),
        )

    def put_item(
            self,
            item: T,
            return_values: ReturnValues = ReturnValues.NONE,
            return_consumed_capacity: ConsumedCapacity = ConsumedCapacity.NONE,
            expression_attribute_names: ExpressionAttributeNames | None = None, # TODO: this shouldn't be needed?
            expression_attribute_values: ExpressionAttributeValues | None = None, # TODO: this shouldn't be needed?
            return_values_on_condition_check_failure: ReturnValues = ReturnValues.NONE,
    ):
        aws_args = dict(
            Item=item.model_dump(),
            ReturnValues=return_values.value,
            ReturnConsumedCapacity=return_consumed_capacity.value,
            ReturnValuesOnConditionCheckFailure=return_values_on_condition_check_failure.value,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
        )
        return self._table.put_item(**aws_args)

        