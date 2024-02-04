import pytest

from kiu_shipping import ShippingManager


@pytest.fixture
def manager() -> ShippingManager:
    return ShippingManager()

