import pytest
import requests

from tests.helpers import (
    create_shop,
    set_business_hours,
    create_barbers,
    set_barber_hours,
    create_services,
    create_customers,
)


@pytest.fixture
def session():
    session = requests.Session()

    yield session

    session.close()


@pytest.fixture
def shop(session):
    shop = create_shop(session)

    yield shop

    shop_id = shop["id"]

    response = session.delete(
        f"http://127.0.0.1:8000/shops/{shop_id}"
    )

    if response.status_code not in (200, 204, 404):
        print(
            f"WARNING: Failed to cleanup shop {shop_id}: "
            f"{response.status_code} {response.text}"
        )


@pytest.fixture
def shop_id(shop):
    return shop["id"]


@pytest.fixture
def configured_shop(session, shop_id):
    set_business_hours(session, shop_id)

    return shop_id


@pytest.fixture
def barbers(session, configured_shop):
    return create_barbers(session, configured_shop)


@pytest.fixture
def configured_barbers(session, configured_shop, barbers):
    set_barber_hours(
        session,
        barbers["barber_1_id"],
        barbers["barber_2_id"],
    )

    return barbers


@pytest.fixture
def services(session, configured_shop):
    return create_services(session, configured_shop)


@pytest.fixture
def customers(session, configured_shop):
    return create_customers(session, configured_shop)


@pytest.fixture
def scheduled_environment(
    session,
    configured_shop,
    configured_barbers,
    services,
    customers,
):
    return {
        "shop_id": configured_shop,

        "barber_1_id": configured_barbers["barber_1_id"],
        "barber_2_id": configured_barbers["barber_2_id"],

        "service_1_id": services["service_1_id"],
        "service_2_id": services["service_2_id"],

        "customer_1_id": customers["customer_1_id"],
        "customer_2_id": customers["customer_2_id"],
    }