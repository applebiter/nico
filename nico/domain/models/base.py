"""Base classes and types for domain entities."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class Entity:
    """Base class for all domain entities with identity."""

    def __init__(self, id: Optional[UUID] = None):
        self.id = id or uuid4()
        self.created_at = datetime.utcnow()
        self.modified_at = datetime.utcnow()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


class ValueObject:
    """Base class for value objects (immutable, compared by value)."""

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __hash__(self) -> int:
        return hash(tuple(sorted(self.__dict__.items())))
