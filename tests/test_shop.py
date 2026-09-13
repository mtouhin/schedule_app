from tests.helpers import BASE_URL, check


def test_create_and_get_shop(session, shop):
    shop_id = shop["id"]

    response = session.get(
        f"{BASE_URL}/shops/{shop_id}"
    )

    check(
        response,
        200,
        "Retrieve shop",
    )

    result = response.json()

    assert result["id"] == shop_id
    assert result["name"] == "TEST - Barber Shop"
    assert result["address"] == "123 Test Street, Dallas, TX"


def test_nonexistent_shop(session):
    response = session.get(
        f"{BASE_URL}/shops/"
        "00000000-0000-0000-0000-000000000000"
    )

    check(
        response,
        404,
        "Reject nonexistent shop",
    )