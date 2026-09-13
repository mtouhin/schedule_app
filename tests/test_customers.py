from tests.helpers import BASE_URL, check


def test_create_customers(
    session,
    configured_shop,
):
    response = session.post(
        f"{BASE_URL}/shops/{configured_shop}/customers",
        json={
            "name": "Alice",
            "phone": "2145555001",
            "email": "alice@test.com",
        },
    )

    check(response, 200, "Create Alice")

    customer = response.json()

    assert customer["name"] == "Alice"


def test_duplicate_customer_phone(
    session,
    configured_shop,
    customers,
):
    response = session.post(
        f"{BASE_URL}/shops/{configured_shop}/customers",
        json={
            "name": "Alice Again",
            "phone": "2145555001",
            "email": "different@test.com",
        },
    )

    check(
        response,
        409,
        "Reject duplicate customer phone",
    )


def test_get_customer_by_phone(
    session,
    configured_shop,
    customers,
):
    response = session.get(
        f"{BASE_URL}/shops/{configured_shop}"
        "/customers/phone/2145555001"
    )

    check(
        response,
        200,
        "Retrieve customer by phone",
    )

    customer = response.json()

    assert customer["name"] == "Alice"
    assert customer["phone"] == "2145555001"