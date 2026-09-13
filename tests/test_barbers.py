from tests.helpers import BASE_URL, check


def test_create_barbers(
    session,
    configured_shop,
):
    response = session.post(
        f"{BASE_URL}/shops/{configured_shop}/barbers",
        json={
            "name": "John",
            "phone": "2145551111",
            "email": "john@test.com",
        },
    )

    check(response, 200, "Create John")

    john = response.json()

    assert john["name"] == "John"


def test_get_barbers(
    session,
    configured_shop,
    barbers,
):
    response = session.get(
        f"{BASE_URL}/shops/{configured_shop}/barbers"
    )

    check(
        response,
        200,
        "Retrieve barbers",
    )

    result = response.json()

    assert len(result) == 2


def test_duplicate_barber_name(
    session,
    configured_shop,
    barbers,
):
    response = session.post(
        f"{BASE_URL}/shops/{configured_shop}/barbers",
        json={
            "name": "John",
            "phone": "2145553333",
            "email": "another@test.com",
        },
    )

    check(
        response,
        409,
        "Reject duplicate barber name",
    )


def test_duplicate_barber_phone(
    session,
    configured_shop,
    barbers,
):
    response = session.post(
        f"{BASE_URL}/shops/{configured_shop}/barbers",
        json={
            "name": "Another Barber",
            "phone": "2145551111",
            "email": "another@test.com",
        },
    )

    check(
        response,
        409,
        "Reject duplicate barber phone",
    )


def test_duplicate_barber_email_case_insensitive(
    session,
    configured_shop,
    barbers,
):
    response = session.post(
        f"{BASE_URL}/shops/{configured_shop}/barbers",
        json={
            "name": "Another Barber",
            "phone": "2145554444",
            "email": "JOHN@TEST.COM",
        },
    )

    check(
        response,
        409,
        "Reject duplicate barber email",
    )