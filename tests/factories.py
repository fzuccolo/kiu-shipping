from typing import List, Optional
from datetime import datetime, timedelta

from kiu_shipping import (
    Client,
    Facility,
    Transport,
    Trip,
    Package,
)

A_WEIGHT = 10


def given_clients(count: int) -> List[Client]:
    """Clients factory for testing."""
    return [Client(name=f"Client{i}") for i in range(count)]


def given_facilities(count: int) -> List[Facility]:
    """Facilities factory for testing."""
    return [
        Facility(name=f"Facility{i}", location=f"Location{i}")
        for i in range(count)
    ]


def given_transports(count: int) -> List[Transport]:
    """Transports factory for testing."""
    return [
        Transport(name=f"Transport{i}", max_weight=50)
        for i in range(count)
    ]


def given_trips(count: int, with_departure_date: Optional[datetime] = None) -> List[Trip]:
    """Trips factory for testing."""
    transports = given_transports(count=count)
    trips = []
    for i in range(count):
        origin, destination = given_facilities(count=2)
        departure_date = with_departure_date or datetime.utcnow()
        arrival_date = departure_date + timedelta(days=2)
        trip = Trip(
            transport=transports[i],
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            arrival_date=arrival_date,
        )
        trips.append(trip)
    return trips


def given_packages(count: int) -> List[Package]:
    clients = given_clients(count)
    facilities = given_facilities(count + 1)
    packages = []
    for i in range(count):
        package = Package(
            sender=clients[i],
            origin=facilities[i],
            destination=facilities[i+1],
            weight=A_WEIGHT,
        )
        packages.append(package)
    return packages


def given_packages_with_same_trip(count: int) -> List[Package]:
    clients = given_clients(count)
    origin, destination = given_facilities(2)
    return [
        Package(
            sender=clients[i],
            origin=origin,
            destination=destination,
            weight=A_WEIGHT,
        )
        for i in range(count)
    ]