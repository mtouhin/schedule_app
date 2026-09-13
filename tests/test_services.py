from tests.helpers import BASE_URL, check


def test_create_services(
    session,
    configured_shop,
):
    response = session.post(
        f"{BASE_URL}/shops/{configured_shop}/services",
        json={
            "name": "Haircut",
            "description": "Standard haircut",
            "duration_minutes": 30,
            "price_cents": 3000,
        },
    )

    check(
        response,
        200,
        "Create haircut service",
    )

    service = response.json()

    assert service["name"] == "Haircut"
    assert service["duration_minutes"] == 30
    assert service["price_cents"] == 3000


def test_get_services(
    session,
    configured_shop,
    services,
):
    response = session.get(
        f"{BASE_URL}/shops/{configured_shop}/services"
    )

    check(
        response,
        200,
        "Retrieve services",
    )

    result = response.json()

    assert len(result) == 2


def test_delete_unused_service(
    session,
    scheduled_environment,
):
    shop_id = scheduled_environment["shop_id"]
    service_id = scheduled_environment["service_2_id"]

    response = session.delete(
        f"{BASE_URL}/shops/{shop_id}/services/{service_id}"
    )

    check(
        response,
        200,
        "Delete unused service",
    )


def test_cannot_delete_service_with_appointments(
    session,
    scheduled_environment,
):
    shop_id = scheduled_environment["shop_id"]

    customer_id = scheduled_environment["customer_1_id"]
    service_id = scheduled_environment["service_1_id"]
    barber_id = scheduled_environment["barber_1_id"]

    response = session.post(
        f"{BASE_URL}/shops/{shop_id}/appointments",
        json={
            "customer_id": customer_id,
            "service_id": service_id,
            "barber_id": barber_id,
            "start_time": "2026-09-07T10:00:00",
            "notes": "Service deletion test",
        },
    )

    check(
        response,
        200,
        "Create appointment using service",
    )

    response = session.delete(
        f"{BASE_URL}/shops/{shop_id}/services/{service_id}"
    )

    check(
        response,
        409,
        "Prevent deleting service with appointments",
    )