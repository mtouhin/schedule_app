from tests.helpers import check, create_appointment

def test_create_appointment(
    session,
    scheduled_environment,
):
    env = scheduled_environment

    response = create_appointment(
        session=session,
        shop_id=env["shop_id"],
        customer_id=env["customer_1_id"],
        service_id=env["service_1_id"],
        barber_id=env["barber_1_id"],
        start_time="2026-09-07T10:00:00",
        notes="Test appointment",
    )

    check(response, 200, "Create appointment")

    appointment = response.json()

    assert appointment["customer_id"] == env["customer_1_id"]
    assert appointment["barber_id"] == env["barber_1_id"]
    assert appointment["service_id"] == env["service_1_id"]

def test_any_barber(
    session,
    scheduled_environment,
):
    env = scheduled_environment

    response = create_appointment(
        session=session,
        shop_id=env["shop_id"],
        customer_id=env["customer_1_id"],
        service_id=env["service_1_id"],
        barber_id=None,
        start_time="2026-09-07T11:00:00",
    )

    check(response, 200, "Book with any available barber")

    appointment = response.json()

    assert appointment["barber_id"] is not None

def test_allow_same_time_different_barber(
    session,
    scheduled_environment,
):
    env = scheduled_environment

    first = create_appointment(
        session=session,
        shop_id=env["shop_id"],
        customer_id=env["customer_1_id"],
        service_id=env["service_1_id"],
        barber_id=env["barber_1_id"],
        start_time="2026-09-07T10:00:00",
    )

    check(first, 200, "Create John's appointment")

    response = create_appointment(
        session=session,
        shop_id=env["shop_id"],
        customer_id=env["customer_2_id"],
        service_id=env["service_1_id"],
        barber_id=env["barber_2_id"],
        start_time="2026-09-07T10:00:00",
    )

    check(response, 200, "Allow same time for different barber")