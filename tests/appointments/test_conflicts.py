from tests.helpers import (
    check,
    create_appointment,
)

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

def test_allow_same_time_for_different_barbers(
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
        "Create John's appointment",
    )

    response = create_appointment(
        session=session,
        shop_id=env["shop_id"],
        customer_id=env["customer_2_id"],
        service_id=env["service_1_id"],
        barber_id=env["barber_2_id"],
        start_time="2026-09-07T10:00:00",
    )

    check(
        response,
        200,
        "Allow same time for different barber",
    )

def test_reject_multiple_overlapping_appointments(
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
        start_time="2026-09-07T10:30:00",
    )

    check(
        second,
        200,
        "Create second back-to-back appointment",
    )

    response = create_appointment(
        session=session,
        shop_id=env["shop_id"],
        customer_id=env["customer_1_id"],
        service_id=env["service_1_id"],
        barber_id=env["barber_1_id"],
        start_time="2026-09-07T10:15:00",
    )

    check(
        response,
        400,
        "Reject appointment overlapping existing appointments",
    )