from dataclasses import dataclass
from typing import Generic, TypeVar

from mypy_boto3_dynamodb.type_defs import ConsumedCapacityTypeDef

from ek.model import EntityModel

T = TypeVar("T", bound=EntityModel)


@dataclass
class CapacityResponse:
    capacity_units: float | None
    read_capacity_units: float | None
    write_capacity_units: float | None


@dataclass
class ConsumedCapacityResponse:
    capacity_units: float | None
    global_secondary_indexes: dict[str, CapacityResponse]
    local_secondary_indexes: dict[str, CapacityResponse]
    read_capacity_units: float | None
    table: CapacityResponse
    table_name: str | None
    write_capacity_units: float | None

    @classmethod
    def from_ddb(
        cls, consumed_capacity: ConsumedCapacityTypeDef | None
    ) -> "ConsumedCapacityResponse | None":
        if not consumed_capacity:
            return None
        return cls(
            capacity_units=consumed_capacity.get("CapacityUnits"),
            global_secondary_indexes={
                index_name: CapacityResponse(
                    capacity_units=gsi.get("CapacityUnits"),
                    read_capacity_units=gsi.get("ReadCapacityUnits"),
                    write_capacity_units=gsi.get("WriteCapacityUnits"),
                )
                for index_name, gsi in consumed_capacity.get(
                    "GlobalSecondaryIndexes", {}
                ).items()
            },
            local_secondary_indexes={
                index_name: CapacityResponse(
                    capacity_units=lsi.get("CapacityUnits"),
                    read_capacity_units=lsi.get("ReadCapacityUnits"),
                    write_capacity_units=lsi.get("WriteCapacityUnits"),
                )
                for index_name, lsi in consumed_capacity.get(
                    "LocalSecondaryIndexes", {}
                ).items()
            },
            read_capacity_units=consumed_capacity.get("ReadCapacityUnits"),
            table=CapacityResponse(
                capacity_units=consumed_capacity.get("Table", {}).get("CapacityUnits"),
                read_capacity_units=consumed_capacity.get("Table", {}).get(
                    "ReadCapacityUnits"
                ),
                write_capacity_units=consumed_capacity.get("Table", {}).get(
                    "WriteCapacityUnits"
                ),
            ),
            table_name=consumed_capacity.get("TableName"),
            write_capacity_units=consumed_capacity.get("WriteCapacityUnits"),
        )


@dataclass(frozen=True, slots=True)
class GetItemResponse(Generic[T]):
    item: T | None
    consumed_capacity: ConsumedCapacityResponse | None = None


@dataclass(frozen=True, slots=True)
class PutItemResponse(Generic[T]):
    item: T | None
    consumed_capacity: ConsumedCapacityResponse | None = None


@dataclass(frozen=True, slots=True)
class QueryResponse(Generic[T]):
    items: list[T]
    consumed_capacity: ConsumedCapacityResponse | None = None
