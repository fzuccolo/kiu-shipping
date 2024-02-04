from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Set
from uuid import uuid4

from .constants import FLAT_PRICE
from .exceptions import (
    InsufficientCapacityError,
    DepartureAfterArrivalError,
    SameOriginDestinationError,
)


@dataclass(frozen=True)
class Client:
    """A client that deliver packages."""
    name: str
    registration_date: datetime = field(init=False, default_factory=datetime.utcnow)


@dataclass(frozen=True)
class Facility:
    """A storage facility for sending and receiving packages."""
    name: str
    location: str


@dataclass(frozen=True)
class Package:
    """A package that must be delivered."""
    sender: Client
    origin: Facility
    destination: Facility
    weight: int
    track_id: str = field(init=False, default_factory=lambda: str(uuid4()))
    admission_date: datetime = field(init=False, default_factory=datetime.utcnow)

    def __post_init__(self):
        self._validate_fields()

    def _validate_fields(self) -> None:
        """Check that initialization fields are valid."""
        if self.origin.location == self.destination.location:
            raise SameOriginDestinationError("Package can not be sent to its origin.")

    def get_price(self):
        """Get price to charge for delivering this package."""
        return FLAT_PRICE


@dataclass(frozen=True)
class Transport:
    """Aereal transport with package delivery capabilities."""
    name: str
    max_weight: int


@dataclass
class Trip:
    """A trip between facilities using an available transport."""
    transport: Transport
    origin: Facility
    destination: Facility
    departure_date: datetime
    arrival_date: datetime
    packages: Set[Package] = field(default_factory=set, init=False)

    def __post_init__(self):
        self._validate_fields()

    def _validate_fields(self) -> None:
        """Check that initialization fields are logically valid."""
        if self.arrival_date < self.departure_date:
            raise DepartureAfterArrivalError("Departure date can not be greater than arrival date")
        if self.destination.name == self.origin.name:
            raise SameOriginDestinationError("Packages has same origin and destination")

    def can_add_package(self, package: Package) -> bool:
        """Check if package can be delivered in this trip."""
        required_weight = package.weight + sum(pack.weight for pack in self.packages)
        return required_weight <= self.transport.max_weight

    def add_package(self, package: Package) -> None:
        """Add a new package to be delivered in this trip."""
        if not self.can_add_package(package):
            raise InsufficientCapacityError("The transport of this trip can't deliver this package")
        self.packages.add(package)

    def overlaps_with(self, other: Trip) -> bool:
        """Check that transport is not assigned to other trip in overlapping dates."""
        if self.transport != other.transport:
            return False
        if self.arrival_date < other.departure_date or self.departure_date > other.arrival_date:
            return False
        return True
