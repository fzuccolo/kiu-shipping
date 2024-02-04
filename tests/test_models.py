from datetime import datetime, timedelta

import pytest

from kiu_shipping import Package, Trip
from kiu_shipping.exceptions import (
    DepartureAfterArrivalError,
    InsufficientCapacityError,
    SameOriginDestinationError,
)

from .factories import (
    given_clients,
    given_facilities,
    given_transports,
    given_trips,
)


def test_package_can_not_have_same_origin_and_destination():
    facility, = given_facilities(count=1)
    client, = given_clients(count=1)

    with pytest.raises(SameOriginDestinationError):
        Package(
            sender=client,
            origin=facility,
            destination=facility,
            weight=1,
        )


def test_trip_invalid_dates():
    transport, = given_transports(count=1)
    origin, destination = given_facilities(count=2)
    departure_date = datetime.utcnow()
    arrival_date = departure_date - timedelta(days=1)

    with pytest.raises(DepartureAfterArrivalError):
        Trip(
            transport=transport,
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            arrival_date=arrival_date,
        )


def test_trip_invalid_origin_destination():
    transport, = given_transports(count=1)
    facility, = given_facilities(count=1)
    departure_date = datetime.utcnow()
    arrival_date = departure_date + timedelta(days=1)

    with pytest.raises(SameOriginDestinationError):
        Trip(
            transport=transport,
            origin=facility,
            destination=facility,
            departure_date=departure_date,
            arrival_date=arrival_date,
        )


def test_trip_with_same_transport_not_overlapping():
    date = datetime.utcnow()
    trip_1, trip_2 = given_trips(count=2)
    trip_1.transport = trip_2.transport
    trip_1.departure_date = date
    trip_1.arrival_date = date + timedelta(days=1)
    trip_2.departure_date = date + timedelta(days=2)
    trip_2.arrival_date = date + timedelta(days=3)

    assert trip_1.overlaps_with(trip_2) is False


def test_overweighted_package_can_not_be_added_to_trip():
    trip, = given_trips(count=1)
    origin, destination = given_facilities(count=2)
    client, = given_clients(count=1)
    overweight = 2 * trip.transport.max_weight
    package = Package(
        sender=client,
        origin=origin,
        destination=destination,
        weight=overweight,
    )

    with pytest.raises(InsufficientCapacityError):
        trip.add_package(package)
