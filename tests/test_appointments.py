from tests.helpers import (
    BASE_URL,
    check,
    create_appointment,
    get_availability,
)

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

    check(
        response,
        200,
        "Create appointment",
    )

    appointment = response.json()

    assert appointment["customer_id"] == env["customer_1_id"]
    assert appointment["barber_id"] == env["barber_1_id"]
    assert appointment["service_id"] == env["service_1_id"]

def test_reject_double_booking(
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

    check(
        first,
        200,
        "Create first appointment",
    )

    response = create_appointment(
        session=session,
        shop_id=env["shop_id"],
        customer_id=env["customer_2_id"],
        service_id=env["service_1_id"],
        barber_id=env["barber_1_id"],
        start_time="2026-09-07T10:00:00",
        notes="Should fail",
    )

    check(
        response,
        400,
        "Reject double booking",
    )

def test_allow_back_to_back_appointment(
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

    check(
        first,
        200,
        "Create first appointment",
    )

    response = create_appointment(
        session=session,
        shop_id=env["shop_id"],
        customer_id=env["customer_2_id"],
        service_id=env["service_1_id"],
        barber_id=env["barber_1_id"],
        start_time="2026-09-07T10:30:00",
        notes="Back-to-back",
    )

    check(
        response,
        200,
        "Allow back-to-back appointment",
    )

def test_reject_overlapping_appointment(
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
        start_time="2026-09-07T10:30:00",
    )

    check(
        first,
        200,
        "Create existing appointment",
    )

    response = create_appointment(
        session=session,
        shop_id=env["shop_id"],
        customer_id=env["customer_2_id"],
        service_id=env["service_1_id"],
        barber_id=env["barber_1_id"],
        start_time="2026-09-07T10:15:00",
        notes="Should fail",
    )

    check(
        response,
        400,
        "Reject overlapping appointment",
    )

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
        notes="Any barber",
    )

    check(
        response,
        200,
        "Book with any available barber",
    )

    appointment = response.json()

    assert appointment["barber_id"] is not None

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

    check(response, 200, "Create appointment")

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

    check(response, 200, "Create appointment")

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

    check(response, 200, "Create appointment")

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

    assert len(appointments) >= 1

def test_reschedule_appointment(
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

    check(response, 200, "Create appointment")

    appointment_id = response.json()["id"]

    response = session.patch(
        f"{BASE_URL}/shops/{env['shop_id']}"
        f"/appointments/{appointment_id}",
        json={
            "start_time": "2026-09-07T11:30:00",
        },
    )

    check(
        response,
        200,
        "Reschedule appointment",
    )

    result = response.json()

    assert "11:30:00" in result["start_time"]

def test_reassign_appointment(
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
        start_time="2026-09-07T11:30:00",
    )

    check(response, 200, "Create appointment")

    appointment_id = response.json()["id"]

    response = session.patch(
        f"{BASE_URL}/shops/{env['shop_id']}"
        f"/appointments/{appointment_id}",
        json={
            "barber_id": env["barber_2_id"],
        },
    )

    check(
        response,
        200,
        "Reassign appointment to Mike",
    )

    result = response.json()

    assert result["barber_id"] == env["barber_2_id"]


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

    check(response, 200, "Create appointment")

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

    appointments = response.json()["appointments"]
    
    for appointment in appointments:
        assert appointment["barber_id"] == env["barber_1_id"]

def test_appointment_statuses(
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

    check(response, 200, "Create appointment")

    appointment_id = response.json()["id"]

    statuses = [
        "CONFIRMED",
        "RUNNING_LATE",
        "COMPLETED",
    ]

    for status in statuses:
        response = session.patch(
            f"{BASE_URL}/shops/{env['shop_id']}"
            f"/appointments/{appointment_id}/status",
            json={
                "status": status,
            },
        )

        check(
            response,
            200,
            f"Set appointment status to {status}",
        )

def test_cancel_appointment(
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
        start_time="2026-09-07T13:00:00",
        notes="Cancellation test",
    )

    check(
        response,
        200,
        "Create appointment for cancellation test",
    )

    appointment_id = response.json()["id"]

    response = session.patch(
        f"{BASE_URL}/shops/{env['shop_id']}"
        f"/appointments/{appointment_id}/status",
        json={
            "status": "CANCELLED",
        },
    )

    check(
        response,
        200,
        "Cancel appointment",
    )

def test_cancellation_frees_slot(
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
        start_time="2026-09-07T13:00:00",
    )

    check(response, 200, "Create appointment")

    appointment_id = response.json()["id"]

    response = session.patch(
        f"{BASE_URL}/shops/{env['shop_id']}"
        f"/appointments/{appointment_id}/status",
        json={
            "status": "CANCELLED",
        },
    )

    check(
        response,
        200,
        "Cancel appointment",
    )

    response = get_availability(
        session,
        env["shop_id"],
        env["service_1_id"],
        "2026-09-07",
        env["barber_1_id"],
    )

    check(
        response,
        200,
        "Check availability after cancellation",
    )

    slots = response.json()["available_times"]

    slot_times = [slot["time"] for slot in slots]

    assert "13:00:00" in slot_times