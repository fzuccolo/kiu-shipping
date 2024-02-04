from datetime import date, datetime, timedelta

import pytest

from kiu_shipping import (
    Trip,
    Package,
)
from kiu_shipping.constants import FLAT_PRICE
from kiu_shipping.exceptions import (
    NoTripAvailableForPackage,
    PackageAlreadyScheduledError,
    RecordExistsError,
    TripOverlapError,
    UnregisteredClientError,
)

from .factories import (
    given_clients,
    given_facilities,
    given_packages_with_same_trip,
    given_packages,
    given_transports,
    given_trips,
)

A_DATE = datetime.utcnow()


def test_clients_added_to_the_system_are_registered_clients(manager):
    client_1, client_2 = given_clients(count=2)

    manager.add_client(client_1)
    manager.add_client(client_2)

    assert manager.has_client(client_1) is True
    assert manager.has_client(client_2) is True


def test_clients_not_added_to_the_system_are_not_registered_clients(manager):
    client_1, client_2 = given_clients(count=2)

    assert manager.has_client(client_1) is False
    assert manager.has_client(client_2) is False


def test_registered_clients_can_not_be_registered_again(manager):
    client, = given_clients(count=1)
    manager.add_client(client)

    with pytest.raises(RecordExistsError):
        manager.add_client(client)


def test_facilities_can_be_added_to_the_system(manager):
    facility_1, facility_2 = given_facilities(count=2)

    manager.add_facility(facility_1)
    manager.add_facility(facility_2)

    assert manager.has_facility(facility_1) is True
    assert manager.has_facility(facility_2) is True


def test_facility_is_not_registered_in_the_system(manager):
    facility, = given_facilities(count=1)

    assert manager.has_facility(facility) is False


def test_same_facility_can_not_be_added_twice(manager):
    facility, = given_facilities(count=1)
    manager.add_facility(facility)

    with pytest.raises(RecordExistsError):
        manager.add_facility(facility)


def test_transports_can_be_added_to_the_system(manager):
    transport_1, transport_2 = given_transports(count=2)

    manager.add_transport(transport_1)
    manager.add_transport(transport_2)

    assert manager.has_transport(transport_1) is True
    assert manager.has_transport(transport_2) is True


def test_transport_is_not_registered_in_the_system(manager):
    transport, = given_transports(count=1)

    assert manager.has_transport(transport) is False


def test_transport_can_not_be_added_twice(manager):
    transport, = given_transports(count=1)
    manager.add_transport(transport)

    with pytest.raises(RecordExistsError):
        manager.add_transport(transport)


def test_trips_can_be_added_to_the_system(manager):
    trip_1, trip_2 = given_trips(count=2)

    manager.add_trip(trip_1)
    manager.add_trip(trip_2)

    assert manager.has_trip(trip_1) is True
    assert manager.has_trip(trip_2) is True


def test_overlapping_trips_can_not_be_added_to_the_system(manager):
    trip, = given_trips(count=1)
    manager.add_trip(trip)

    with pytest.raises(TripOverlapError):
        manager.add_trip(trip)


def test_packages_can_not_be_added_without_registering_client(manager):
    package, = given_packages(count=1)

    with pytest.raises(UnregisteredClientError):
        manager.add_package(package)


def test_packages_can_not_be_added_without_available_trips(manager):
    package, = given_packages(count=1)
    manager.add_client(package.sender)

    with pytest.raises(NoTripAvailableForPackage):
        manager.add_package(package)


def test_packages_can_be_added_to_the_system(manager):
    package, = given_packages(count=1)
    transport, = given_transports(count=1)
    trip = Trip(
        transport=transport,
        origin=package.origin,
        destination=package.destination,
        departure_date=A_DATE + timedelta(hours=2),
        arrival_date=A_DATE + timedelta(days=2),
    )
    manager.add_client(package.sender)
    manager.add_trip(trip)

    manager.add_package(package)

    assert manager.has_package(package)


def test_same_packages_can_not_be_scheduled_twice(manager):
    package, = given_packages(count=1)
    transport, = given_transports(count=1)
    trip = Trip(
        transport=transport,
        origin=package.origin,
        destination=package.destination,
        departure_date=A_DATE + timedelta(hours=2),
        arrival_date=A_DATE + timedelta(days=2),
    )
    manager.add_client(package.sender)
    manager.add_trip(trip)
    manager.add_package(package)

    with pytest.raises(PackageAlreadyScheduledError):
        manager.add_package(package)


def test_package_can_not_be_added_to_trip_if_is_overweighted(manager):
    trip, = given_trips(count=1)
    overweight = 2 * trip.transport.max_weight
    client, = given_clients(count=1)
    package = Package(
        sender=client,
        origin=trip.origin,
        destination=trip.destination,
        weight=overweight,
    )
    manager.add_client(package.sender)
    manager.add_trip(trip)

    with pytest.raises(NoTripAvailableForPackage):
        manager.add_package(package)


@pytest.mark.parametrize("date", (
    date(2024, 1, 4),
    date(2022, 12, 31),
    date(2099, 6, 13),
))
def test_get_empty_daily_report(date, manager):
    report = manager.get_daily_report(date)

    assert report == {
        "date": str(date),
        "packages": 0,
        "earnings": 0,
    }


@pytest.mark.parametrize("package_count", (7, 16, 25))
def test_get_daily_report_with_earnings(manager, package_count):
    departure_date = A_DATE + timedelta(days=1)
    packages = given_packages_with_same_trip(count=package_count)
    trips = given_trips(count=10, with_departure_date=departure_date)
    for trip in trips:
        trip.origin = packages[0].origin
        trip.destination = packages[0].destination
        manager.add_trip(trip)
    for package in packages:
        manager.add_client(package.sender)
        manager.add_package(package)

    report = manager.get_daily_report(departure_date.date())

    assert report == {
        "date": str(departure_date.date()),
        "packages": package_count,
        "earnings": package_count * FLAT_PRICE,
    }
