from tests.helpers import (
    BASE_URL,
    check,
    create_appointment,
    get_availability,
)

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
            json={"status": status},
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
        json={"status": "CANCELLED"},
    )

    check(
        response,
        200,
        "Cancel appointment",
    )

    result = response.json()

    assert result["status"] == "CANCELLED"

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
        notes="Cancellation test",
    )

    check(response, 200, "Create appointment")

    appointment_id = response.json()["id"]

    response = session.patch(
        f"{BASE_URL}/shops/{env['shop_id']}"
        f"/appointments/{appointment_id}/status",
        json={"status": "CANCELLED"},
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

    slot_times = [
        slot["time"]
        for slot in slots
    ]

    assert "13:00:00" in slot_times