from collections import UserDict
from collections.abc import Callable, Generator
from dataclasses import dataclass
from typing import Any, Generic, TypeVar


@dataclass
class Model:
    field: Any


@dataclass
class EntryV1(Model):
    field: int


@dataclass
class EntryV2(Model):
    field: str


@dataclass
class EntryV3(Model):
    field: str


T = TypeVar("T", bound=Model)
U = TypeVar("U", bound=Model)


class ConversionDict(UserDict[type[Model], Callable[[Any], T]]):
    def __setitem__(self, key: type[U], value: Callable[[U], T]) -> None:
        return super().__setitem__(key, value)

    def __getitem__(self, key: type[U]) -> Callable[[U], T]:
        return super().__getitem__(key)


class Store(Generic[T]):
    def __init__(self, model: type[T], entries: list[Model]) -> None:
        self.model = model
        self.entries = entries
        self.converters: ConversionDict[T] = ConversionDict()

    def register_converter(self, old: type[U], converter: Callable[[U], T]) -> None:
        self.converters[old] = converter

    def _convert(self, entry: Model) -> T:
        if isinstance(entry, self.model):
            return entry
        else:
            converter = self.converters[entry.__class__]
            return converter(entry)

    def get(self, idx: int) -> T:
        return self._convert(self.entries[idx])

    def get_all(self) -> Generator[T, None, None]:
        return (self._convert(entry) for entry in self.entries)


store = Store(EntryV2, [EntryV1(field=1), EntryV2(field="2")])


def converter(entry: EntryV1) -> EntryV2:
    return EntryV2(field=str(entry.field))


store.register_converter(EntryV1, converter)
print(store.get(0))
print(list(store.get_all()))
