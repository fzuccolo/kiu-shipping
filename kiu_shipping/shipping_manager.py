from bisect import insort
from datetime import date
from typing import List, Dict, Set

from .exceptions import (
    RecordExistsError,
    TripOverlapError,
    UnregisteredClientError,
    NoTripAvailableForPackage,
    PackageAlreadyScheduledError,
)
from .models import Client, Facility, Package, Transport, Trip


class ShippingManager:
    """Handle all shipping managing actions."""

    def __init__(self):
        self.clients: Dict[str, Client] = {}
        self.facilities: Dict[str, Facility] = {}
        self.transports: Dict[str, Transport] = {}
        self.trips: List[Trip] = []
        self.tracked_packages: Set[str] = set()

    def add_client(self, client: Client) -> None:
        """Add a new client to the system."""
        if self.has_client(client):
            raise RecordExistsError(f'Client "{client.name}" already exists')
        self.clients[client.name] = client

    def has_client(self, client: Client) -> bool:
        """Check if given client is already registered in the system."""
        return client.name in self.clients

    def add_facility(self, facility: Facility) -> None:
        """Add a new facility to the system."""
        if self.has_facility(facility):
            raise RecordExistsError(f'Facility "{facility.name}" already exists')
        self.facilities[facility.name] = facility

    def has_facility(self, facility: Facility) -> bool:
        """Check if given facility is already registered in the system."""
        return facility.name in self.facilities

    def add_transport(self, transport: Transport) -> None:
        """Add a new transport to the system."""
        if self.has_transport(transport):
            raise RecordExistsError(f'Transport "{transport.name}" already exists')
        self.transports[transport.name] = transport

    def has_transport(self, transport: Transport) -> bool:
        """Check if given transport is already registered in the system."""
        return transport.name in self.transports

    def add_trip(self, trip: Trip) -> None:
        """Add a new trip to the system."""
        if any(trip.overlaps_with(existing_trip) for existing_trip in self.trips):
            raise TripOverlapError("Given trip is incompatible with existing trips.")
        insort(self.trips, trip, key=lambda trip: trip.departure_date)

    def has_trip(self, trip: Trip) -> None:
        """Check if the given trip is already in the system."""
        return trip in self.trips

    def add_package(self, package: Package) -> None:
        """Add a package to the system if delivery is possible."""
        if not self.has_client(package.sender):
            raise UnregisteredClientError(f'Client "{package.sender}" must be registered to deliver packages')
        self._assign_package_to_trip(package)
        self.tracked_packages.add(package.track_id)

    def has_package(self, package: Package) -> bool:
        """Check if package is already scheduled for delivery."""
        return package.track_id in self.tracked_packages

    def _assign_package_to_trip(self, package: Package) -> None:
        """Automatically assign a package to the next available trip."""
        if self.has_package(package):
            raise PackageAlreadyScheduledError("Can not schedule same package twice")
        try:
            matching_trip = next(
                trip for trip in self.trips
                if trip.can_add_package(package)
                and trip.departure_date > package.admission_date
            )
        except StopIteration:
            raise NoTripAvailableForPackage("This package can not be delivered with the available trips.")
        matching_trip.add_package(package)

    def get_daily_report(self, date: date) -> dict:
        """Generate report containing earnings of the given date."""
        report_data = {
            "date": str(date),
            "packages": 0,
            "earnings": 0,
        }
        for trip in self.trips:
            if trip.departure_date.date() == date:
                report_data["packages"] += len(trip.packages)
                report_data["earnings"] += sum(package.get_price() for package in trip.packages)
        return report_data
