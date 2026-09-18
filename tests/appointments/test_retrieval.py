from tests.helpers import (
    BASE_URL,
    check,
    create_appointment,
)

def test_get_appointment(
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
    )

    check(
        response,
        200,
        "Create appointment",
    )

    appointment_id = response.json()["id"]

    response = session.get(
        f"{BASE_URL}/shops/{env['shop_id']}"
        f"/appointments/{appointment_id}"
    )

    check(
        response,
        200,
        "Retrieve appointment",
    )

    appointment = response.json()

    assert appointment["id"] == appointment_id

def test_get_shop_appointments(
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
    )

    check(
        response,
        200,
        "Create appointment",
    )

    response = session.get(
        f"{BASE_URL}/shops/{env['shop_id']}/appointments",
        params={
            "date": "2026-09-07",
        },
    )

    check(
        response,
        200,
        "Retrieve shop appointments",
    )

    appointments = response.json()

    if isinstance(appointments, dict):
        appointments = appointments["appointments"]

    assert len(appointments) >= 1

def test_get_barber_appointments(
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
    )

    check(
        response,
        200,
        "Create appointment",
    )

    response = session.get(
        f"{BASE_URL}/barbers/{env['barber_1_id']}/appointments",
        params={
            "date": "2026-09-07",
        },
    )

    check(
        response,
        200,
        "Retrieve John's appointments",
    )

    appointments = response.json()

    if isinstance(appointments, dict):
        appointments = appointments["appointments"]

    assert len(appointments) >= 1

def test_filter_shop_appointments_by_barber(
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
    )

    check(
        response,
        200,
        "Create appointment",
    )

    response = session.get(
        f"{BASE_URL}/shops/{env['shop_id']}/appointments",
        params={
            "date": "2026-09-07",
            "barber_id": env["barber_1_id"],
        },
    )

    check(
        response,
        200,
        "Retrieve shop appointments for John",
    )

    data = response.json()

    if isinstance(data, dict):
        appointments = data["appointments"]
    else:
        appointments = data

    for appointment in appointments:
        assert appointment["barber_id"] == env["barber_1_id"]

def test_filter_shop_appointments_by_date(
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
    )

    check(
        response,
        200,
        "Create appointment",
    )

    response = session.get(
        f"{BASE_URL}/shops/{env['shop_id']}/appointments",
        params={
            "date": "2026-09-08",
        },
    )

    check(
        response,
        200,
        "Retrieve appointments for different date",
    )

    data = response.json()

    if isinstance(data, dict):
        appointments = data["appointments"]
    else:
        appointments = data

    assert len(appointments) == 0