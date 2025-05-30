from __future__ import annotations
from typing import Generic, TypeVar, Iterable, Iterator, Any

from src.data_structures.array import Array # Assuming Array is in this path

T = TypeVar('T')

class Tuple(Generic[T]):
    """Một tuple bất biến (immutable) tùy chỉnh, có thể hash được."""
    def __init__(self, items: Iterable[Any]):
        # Convert iterable to our Array
        temp_list = []
        for item in items:
            temp_list.append(item)
        
        self._items: Array[Any] = Array(len(temp_list))
        for i, item in enumerate(temp_list):
            self._items.set(i, item)
        
        self._hash: int | None = None

    def __getitem__(self, index: int) -> Any:
        if not 0 <= index < len(self._items):
            raise IndexError("Tuple index out of range")
        return self._items.get(index)

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[Any]:
        return iter(self._items)

    def __hash__(self) -> int:
        if self._hash is None:
            elements = []
            for i in range(len(self._items)):
                elements.append(self._items.get(i))
            self._hash = hash(tuple(elements))
        return self._hash

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Tuple):
            return NotImplemented
        if len(self) != len(other):
            return False
        for i in range(len(self)):
            if self[i] != other[i]:
                return False
        return True

    def __repr__(self) -> str:
        elements_str = ", ".join(repr(self._items.get(i)) for i in range(len(self._items)))
        return f"Tuple([{elements_str}])" 