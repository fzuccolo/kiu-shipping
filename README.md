# Kiu Shipping

Your best system for managing aereal shippings.

## Installation

Supported Python versions: `3.10`, `3.11` and `3.12`.

For linux, clone the repo and install package:

    git clone git@github.com:fzuccolo/kiu-shipping.git
    cd ./kiu_shipping
    python3 -m venv venv
    . ./venv/bin/activate
    pip3 install -r requirements_dev.txt
    python setup.py develop

## Usage

```python

from kiu_shipping import ShippingManager, Client, Facility, Transport, Trip, Package

manager = ShippingManager()

# Register clients
client = Client(name="Company Name")
manager.add_client(client)

# Register facilities
facility_a = Facility(name="Name A", location="Location X")
facility_b = Facility(name="Name B", location="Location Y")
manager.add_facility(north_facility)
manager.add_facility(south_facility)

# Register transports
transport = Transport(name="Tango 01", max_weight=10000)  # max_weight in Kg
manager.add_transport(transport)

# Schedule a trip
trip = Trip(transport=transport, origin=south_facility, destination=north_facility, departure_date=date(2024, 2, 28), arrival_date=date(2024, 3, 1))
manager.add_trip(trip)

# Schedule a package
package = Package(sender=client, origin=south_facility, destination=north_facility, weight=500)
manager.add_package(package)

# generate a report
manager.get_daily_report(date(2024, 2, 28))

```

## Testing

With the activated virtual environment, run:

    pytest

or for running tests, flake8 and coverage (currently at 100%) all in one with:

    make test

## Bussiness Decisions

* We only deliver packages of registered clients.
* We only accept packages if we have an availabe slot in a scheduled flight.
* Earnings for each package is considered for its delivery date.

## Next Steps

* Add persistence
* Add more tests for corner cases
* Add more validations
* Implement cancelations
* Implement archiving
* Implement API
* Implement CLI
* Handle admitting packages without scheduling delivery
