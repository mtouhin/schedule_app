from datetime import datetime, time

from tests.helpers import (
    BASE_URL,
    check,
    get_availability,
)

def test_any_barber_availability(
    session,
    scheduled_environment,
):
    env = scheduled_environment

    response = get_availability(
        session,
        env["shop_id"],
        env["service_1_id"],
        "2026-09-07",
    )

    check(
        response,
        200,
        "Get availability",
    )

    availability = response.json()

    assert len(availability["available_times"]) > 0

def test_specific_barber_availability(
    session,
    scheduled_environment,
):
    env = scheduled_environment

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
        "Get John's availability",
    )

    availability = response.json()

    assert len(availability["available_times"]) > 0

def test_closed_day_has_no_availability(
    session,
    scheduled_environment,
):
    env = scheduled_environment

    response = get_availability(
        session,
        env["shop_id"],
        env["service_1_id"],
        "2026-09-09",
    )

    check(
        response,
        200,
        "Check closed-day availability",
    )

    result = response.json()

    assert result["available_times"] == []

def test_full_day_closure_has_no_availability(
    session,
    scheduled_environment,
):
    env = scheduled_environment

    response = session.post(
        f"{BASE_URL}/shops/{env['shop_id']}/closures",
        json={
            "closure_date": "2026-09-10",
            "reason": "Emergency power outage",
            "closure_type": "EMERGENCY",
        },
    )

    check(
        response,
        200,
        "Create closure for availability test",
    )

    response = get_availability(
        session,
        env["shop_id"],
        env["service_1_id"],
        "2026-09-10",
        env["barber_1_id"],
    )

    check(
        response,
        200,
        "Full-day closure returns no availability",
    )

    result = response.json()

    assert result["available_times"] == []

def test_availability_returns_after_closure_deleted(
    session,
    scheduled_environment,
):
    env = scheduled_environment

    response = session.post(
        f"{BASE_URL}/shops/{env['shop_id']}/closures",
        json={
            "closure_date": "2026-09-10",
            "reason": "Temporary closure",
            "closure_type": "EMERGENCY",
        },
    )

    check(response, 200, "Create closure")

    closure_id = response.json()["id"]

    response = session.delete(
        f"{BASE_URL}/shops/{env['shop_id']}/closures/{closure_id}"
    )

    check(
        response,
        200,
        "Delete availability-test closure",
    )

    response = get_availability(
        session,
        env["shop_id"],
        env["service_1_id"],
        "2026-09-10",
        env["barber_1_id"],
    )

    check(
        response,
        200,
        "Availability returns after closure is deleted",
    )

    result = response.json()

    assert len(result["available_times"]) > 0

def test_special_hours_restrict_availability(
    session,
    scheduled_environment,
):
    env = scheduled_environment

    # Tuesday is normally open.
    # We shorten it to 9 AM - 1 PM for this date.
    #
    # Using Tuesday instead of Wednesday is intentional:
    # Wednesday is normally a closed day.
    response = session.post(
        f"{BASE_URL}/shops/{env['shop_id']}/closures",
        json={
            "closure_date": "2026-11-24",
            "start_time": "09:00:00",
            "end_time": "13:00:00",
            "reason": "Day before Thanksgiving",
            "closure_type": "HOLIDAY",
        },
    )

    check(
        response,
        200,
        "Create special-hours date",
    )

    closure_id = response.json()["id"]

    response = get_availability(
        session,
        env["shop_id"],
        env["service_1_id"],
        "2026-11-24",
        env["barber_1_id"],
    )

    check(
        response,
        200,
        "Special-hours date returns restricted availability",
    )

    slots = response.json()["available_times"]

    assert len(slots) > 0

    for slot in slots:
        slot_time = datetime.strptime(
            slot["time"],
            "%H:%M:%S",
        ).time()

        assert slot_time >= time(9, 0)
        assert slot_time < time(13, 0)

    response = session.delete(
        f"{BASE_URL}/shops/{env['shop_id']}/closures/{closure_id}"
    )

    check(
        response,
        200,
        "Delete special-hours date",
    )