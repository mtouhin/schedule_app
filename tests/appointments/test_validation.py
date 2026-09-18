from uuid import uuid4

from tests.helpers import (
    check,
    create_appointment,
)

def test_reject_invalid_customer(
    session,
    scheduled_environment,
):
    env = scheduled_environment

    response = create_appointment(
        session=session,
        shop_id=env["shop_id"],
        customer_id=str(uuid4()),
        service_id=env["service_1_id"],
        barber_id=env["barber_1_id"],
        start_time="2026-09-07T10:00:00",
    )

    check(
        response,
        400,
        "Reject appointment with invalid customer",
    )

def test_reject_invalid_barber(
    session,
    scheduled_environment,
):
    env = scheduled_environment

    response = create_appointment(
        session=session,
        shop_id=env["shop_id"],
        customer_id=env["customer_1_id"],
        service_id=env["service_1_id"],
        barber_id=str(uuid4()),
        start_time="2026-09-07T10:00:00",
    )

    check(
        response,
        400,
        "Reject appointment with invalid barber",
    )

def test_reject_invalid_service(
    session,
    scheduled_environment,
):
    env = scheduled_environment

    response = create_appointment(
        session=session,
        shop_id=env["shop_id"],
        customer_id=env["customer_1_id"],
        service_id=str(uuid4()),
        barber_id=env["barber_1_id"],
        start_time="2026-09-07T10:00:00",
    )

    check(
        response,
        400,
        "Reject appointment with invalid service",
    )

def test_reject_timezone_in_start_time(
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
        start_time="2026-09-07T10:00:00Z",
    )

    check(
        response,
        422,
        "Reject timezone-aware appointment time",
    )

def test_reject_appointment_outside_shop_hours(
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
        start_time="2026-09-09T08:00:00",
    )

    check(
        response,
        400,
        "Reject appointment outside shop hours",
    )

def test_reject_appointment_outside_barber_hours(
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
        start_time="2026-09-07T17:30:00",
    )

    check(
        response,
        400,
        "Reject appointment outside barber hours",
    )

def test_reject_appointment_on_barber_off_day(
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
        start_time="2026-09-09T10:00:00",
    )

    check(
        response,
        400,
        "Reject appointment on barber off day",
    )

def test_reject_past_appointment(
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
        start_time="2020-01-01T10:00:00",
    )

    check(
        response,
        400,
        "Reject appointment in the past",
    )