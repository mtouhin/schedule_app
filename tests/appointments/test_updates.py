from tests.helpers import (
    BASE_URL,
    check,
    create_appointment,
)

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

    check(
        response,
        200,
        "Create appointment",
    )

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

    check(
        response,
        200,
        "Create appointment",
    )

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

def test_reject_reschedule_into_occupied_slot(
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

    second = create_appointment(
        session=session,
        shop_id=env["shop_id"],
        customer_id=env["customer_2_id"],
        service_id=env["service_1_id"],
        barber_id=env["barber_1_id"],
        start_time="2026-09-07T11:00:00",
    )

    check(
        second,
        200,
        "Create second appointment",
    )

    appointment_id = second.json()["id"]

    response = session.patch(
        f"{BASE_URL}/shops/{env['shop_id']}"
        f"/appointments/{appointment_id}",
        json={
            "start_time": "2026-09-07T10:00:00",
        },
    )

    check(
        response,
        409,
        "Reject reschedule into occupied slot",
    )

def test_reject_reassign_to_busy_barber(
    session,
    scheduled_environment,
):
    env = scheduled_environment

    busy = create_appointment(
        session=session,
        shop_id=env["shop_id"],
        customer_id=env["customer_1_id"],
        service_id=env["service_1_id"],
        barber_id=env["barber_2_id"],
        start_time="2026-09-07T10:00:00",
    )

    check(
        busy,
        200,
        "Create Mike's appointment",
    )

    appointment = create_appointment(
        session=session,
        shop_id=env["shop_id"],
        customer_id=env["customer_2_id"],
        service_id=env["service_1_id"],
        barber_id=env["barber_1_id"],
        start_time="2026-09-07T10:00:00",
    )

    check(
        appointment,
        200,
        "Create John's appointment",
    )

    appointment_id = appointment.json()["id"]

    response = session.patch(
        f"{BASE_URL}/shops/{env['shop_id']}"
        f"/appointments/{appointment_id}",
        json={
            "barber_id": env["barber_2_id"],
        },
    )

    check(
        response,
        409,
        "Reject reassignment to busy barber",
    )