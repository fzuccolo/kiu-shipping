class SameOriginDestinationError(Exception):
    """A package can not have its origin as its destination."""


class DepartureAfterArrivalError(Exception):
    """Departure date can not be older than arrival."""


class InsufficientCapacityError(Exception):
    """The capacity is not sufficient for handling a package."""


class RecordExistsError(Exception):
    """The record can not be duplicated."""


class TripOverlapError(Exception):
    """Overlapping trips for same transport."""


class UnregisteredClientError(Exception):
    """Client is not registered."""


class NoTripAvailableForPackage(Exception):
    """No trip can deliver this package."""


class PackageAlreadyScheduledError(Exception):
    """Package is already assigned to a shipping trip."""
