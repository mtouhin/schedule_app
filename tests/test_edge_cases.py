from tests.helpers import (
    BASE_URL,
    check,
    create_appointment,
)

# ============================================================
# SHOP EDGE CASES
# ============================================================

def test_create_shop_with_blank_name(session):
    response = session.post(
        f"{BASE_URL}/shops",
        json={
            "name": "",
            "phone": "2145551234",
            "email": "test@example.com",
            "address": "123 Test Street",
            "timezone": "America/Chicago",
        },
    )

    assert response.status_code == 422

def test_create_shop_with_blank_address(session):
    response = session.post(
        f"{BASE_URL}/shops",
        json={
            "name": "Test Shop",
            "phone": "2145551234",
            "email": "test@example.com",
            "address": "",
            "timezone": "America/Chicago",
        },
    )

    assert response.status_code == 422

def test_get_nonexistent_shop(session):
    fake_shop_id = "00000000-0000-0000-0000-000000000000"

    response = session.get(
        f"{BASE_URL}/shops/{fake_shop_id}"
    )

    assert response.status_code == 404

# ============================================================
# BUSINESS HOURS EDGE CASES
# ============================================================

def test_business_hours_rejects_invalid_time_format(
    session,
    shop_id,
):
    response = session.put(
        f"{BASE_URL}/shops/{shop_id}/business-hours",
        json={
            "day_of_week": 0,
            "open_time": "25:00 PM",
            "close_time": "6:00 PM",
            "is_closed": False,
        },
    )

    assert response.status_code == 422

def test_business_hours_rejects_non_15_minute_increment(
    session,
    shop_id,
):
    response = session.put(
        f"{BASE_URL}/shops/{shop_id}/business-hours",
        json={
            "day_of_week": 0,
            "open_time": "9:10 AM",
            "close_time": "6:00 PM",
            "is_closed": False,
        },
    )

    assert response.status_code == 422

def test_business_hours_rejects_open_before_5am(
    session,
    shop_id,
):
    response = session.put(
        f"{BASE_URL}/shops/{shop_id}/business-hours",
        json={
            "day_of_week": 0,
            "open_time": "4:45 AM",
            "close_time": "6:00 PM",
            "is_closed": False,
        },
    )

    assert response.status_code == 422

def test_business_hours_rejects_close_after_1145pm(
    session,
    shop_id,
):
    response = session.put(
        f"{BASE_URL}/shops/{shop_id}/business-hours",
        json={
            "day_of_week": 0,
            "open_time": "9:00 AM",
            "close_time": "12:00 AM",
            "is_closed": False,
        },
    )

    assert response.status_code == 422

def test_business_hours_rejects_close_before_open(
    session,
    shop_id,
):
    response = session.put(
        f"{BASE_URL}/shops/{shop_id}/business-hours",
        json={
            "day_of_week": 0,
            "open_time": "6:00 PM",
            "close_time": "9:00 AM",
            "is_closed": False,
        },
    )

    assert response.status_code == 422

def test_closed_business_day_allows_null_times(
    session,
    shop_id,
):
    response = session.put(
        f"{BASE_URL}/shops/{shop_id}/business-hours",
        json={
            "day_of_week": 6,
            "open_time": None,
            "close_time": None,
            "is_closed": True,
        },
    )

    assert response.status_code == 200

def test_closed_business_day_rejects_times(
    session,
    shop_id,
):
    response = session.put(
        f"{BASE_URL}/shops/{shop_id}/business-hours",
        json={
            "day_of_week": 6,
            "open_time": "9:00 AM",
            "close_time": "6:00 PM",
            "is_closed": True,
        },
    )

    assert response.status_code == 422

def test_business_hours_reject_invalid_day(
    session,
    shop_id,
):
    response = session.put(
        f"{BASE_URL}/shops/{shop_id}/business-hours",
        json={
            "day_of_week": 7,
            "open_time": "9:00 AM",
            "close_time": "6:00 PM",
            "is_closed": False,
        },
    )

    assert response.status_code == 422

# ============================================================
# BARBER EDGE CASES
# ============================================================

def test_duplicate_barber_name(
    session,
    configured_shop,
    barbers,
):
    response = session.post(
        f"{BASE_URL}/shops/{configured_shop}/barbers",
        json={
            "name": "john",
            "phone": "2145559999",
            "email": "different@test.com",
        },
    )

    assert response.status_code == 409

def test_duplicate_barber_phone(
    session,
    configured_shop,
    barbers,
):
    response = session.post(
        f"{BASE_URL}/shops/{configured_shop}/barbers",
        json={
            "name": "Different Barber",
            "phone": "2145551111",
            "email": "different@test.com",
        },
    )

    assert response.status_code == 409

def test_duplicate_barber_email(
    session,
    configured_shop,
    barbers,
):
    response = session.post(
        f"{BASE_URL}/shops/{configured_shop}/barbers",
        json={
            "name": "Different Barber",
            "phone": "2145559999",
            "email": "john@test.com",
        },
    )

    assert response.status_code == 409

def test_barber_empty_name(
    session,
    configured_shop,
):
    response = session.post(
        f"{BASE_URL}/shops/{configured_shop}/barbers",
        json={
            "name": "",
            "phone": "2145559999",
            "email": "different@test.com",
        },
    )

    assert response.status_code == 422

def test_barber_hours_before_shop_open(
    session,
    configured_barbers,
):
    barber_id = configured_barbers["barber_1_id"]

    response = session.put(
        f"{BASE_URL}/barbers/{barber_id}/hours",
        json={
            "day_of_week": 0,
            "start_time": "8:00 AM",
            "end_time": "5:00 PM",
            "is_off": False,
        },
    )

    assert response.status_code == 400

def test_barber_hours_after_shop_close(
    session,
    configured_barbers,
):
    barber_id = configured_barbers["barber_1_id"]

    response = session.put(
        f"{BASE_URL}/barbers/{barber_id}/hours",
        json={
            "day_of_week": 0,
            "start_time": "9:00 AM",
            "end_time": "7:00 PM",
            "is_off": False,
        },
    )

    assert response.status_code == 400

def test_barber_hours_end_before_start(
    session,
    configured_shop,
    barbers,
):
    barber_id = barbers["barber_1_id"]

    response = session.put(
        f"{BASE_URL}/barbers/{barber_id}/hours",
        json={
            "day_of_week": 0,
            "start_time": "5:00 PM",
            "end_time": "4:00 PM",
            "is_off": False,
        },
    )

    assert response.status_code == 422

def test_barber_off_day_allows_null_times(
    session,
    configured_barbers,
):
    barber_id = configured_barbers["barber_1_id"]

    response = session.put(
        f"{BASE_URL}/barbers/{barber_id}/hours",
        json={
            "day_of_week": 2,
            "start_time": None,
            "end_time": None,
            "is_off": True,
        },
    )

    assert response.status_code == 200

# ============================================================
# SERVICE EDGE CASES
# ============================================================

def test_service_rejects_zero_duration(
    session,
    configured_shop,
):
    response = session.post(
        f"{BASE_URL}/shops/{configured_shop}/services",
        json={
            "name": "Invalid Service",
            "description": "Invalid",
            "duration_minutes": 0,
            "price_cents": 3000,
        },
    )

    assert response.status_code == 422

def test_service_rejects_negative_duration(
    session,
    configured_shop,
):
    response = session.post(
        f"{BASE_URL}/shops/{configured_shop}/services",
        json={
            "name": "Invalid Service",
            "description": "Invalid",
            "duration_minutes": -30,
            "price_cents": 3000,
        },
    )

    assert response.status_code == 422

def test_service_rejects_negative_price(
    session,
    configured_shop,
):
    response = session.post(
        f"{BASE_URL}/shops/{configured_shop}/services",
        json={
            "name": "Invalid Service",
            "description": "Invalid",
            "duration_minutes": 30,
            "price_cents": -1,
        },
    )

    assert response.status_code == 422

def test_service_empty_name(
    session,
    configured_shop,
):
    response = session.post(
        f"{BASE_URL}/shops/{configured_shop}/services",
        json={
            "name": "",
            "description": "Invalid",
            "duration_minutes": 30,
            "price_cents": 3000,
        },
    )

    assert response.status_code == 422

# ============================================================
# CUSTOMER EDGE CASES
# ============================================================

def test_duplicate_customer_phone(
    session,
    configured_shop,
    customers,
):
    response = session.post(
        f"{BASE_URL}/shops/{configured_shop}/customers",
        json={
            "name": "Different Person",
            "phone": "2145555001",
            "email": "different@test.com",
        },
    )

    assert response.status_code == 409

def test_customer_empty_name(
    session,
    configured_shop,
):
    response = session.post(
        f"{BASE_URL}/shops/{configured_shop}/customers",
        json={
            "name": "",
            "phone": "2145554444",
            "email": "test@test.com",
        },
    )

    assert response.status_code == 422

def test_customer_empty_phone(
    session,
    configured_shop,
):
    response = session.post(
        f"{BASE_URL}/shops/{configured_shop}/customers",
        json={
            "name": "Test Customer",
            "phone": "",
            "email": "test@test.com",
        },
    )

    assert response.status_code == 422

# ============================================================
# AVAILABILITY EDGE CASES
# ============================================================

def test_availability_for_nonexistent_service(
    session,
    configured_shop,
):
    fake_service_id = "00000000-0000-0000-0000-000000000000"

    response = session.get(
        f"{BASE_URL}/shops/{configured_shop}/availability",
        params={
            "service_id": fake_service_id,
            "date": "2026-09-07",
        },
    )

    assert response.status_code == 400

def test_availability_for_nonexistent_barber(
    session,
    configured_shop,
    services,
):
    fake_barber_id = "00000000-0000-0000-0000-000000000000"

    response = session.get(
        f"{BASE_URL}/shops/{configured_shop}/availability",
        params={
            "service_id": services["service_1_id"],
            "date": "2026-09-07",
            "barber_id": fake_barber_id,
        },
    )

    assert response.status_code == 400

def test_availability_on_closed_day(
    session,
    configured_shop,
    services,
):
    response = session.get(
        f"{BASE_URL}/shops/{configured_shop}/availability",
        params={
            "service_id": services["service_1_id"],
            "date": "2026-09-09",
        },
    )

    check(
        response,
        200,
        "Availability on closed day",
    )

    data = response.json()

    assert data["available_times"] == []

# ============================================================
# APPOINTMENT VALIDATION
# ============================================================

def test_appointment_with_nonexistent_customer(
    session,
    scheduled_environment,
):
    env = scheduled_environment

    fake_customer_id = "00000000-0000-0000-0000-000000000000"

    response = create_appointment(
        session=session,
        shop_id=env["shop_id"],
        customer_id=fake_customer_id,
        service_id=env["service_1_id"],
        barber_id=env["barber_1_id"],
        start_time="2026-09-07T10:00:00",
    )

    assert response.status_code == 400

def test_appointment_with_nonexistent_service(
    session,
    scheduled_environment,
):
    env = scheduled_environment

    fake_service_id = "00000000-0000-0000-0000-000000000000"

    response = create_appointment(
        session=session,
        shop_id=env["shop_id"],
        customer_id=env["customer_1_id"],
        service_id=fake_service_id,
        barber_id=env["barber_1_id"],
        start_time="2026-09-07T10:00:00",
    )

    assert response.status_code == 400

def test_appointment_with_nonexistent_barber(
    session,
    scheduled_environment,
):
    env = scheduled_environment

    fake_barber_id = "00000000-0000-0000-0000-000000000000"

    response = create_appointment(
        session=session,
        shop_id=env["shop_id"],
        customer_id=env["customer_1_id"],
        service_id=env["service_1_id"],
        barber_id=fake_barber_id,
        start_time="2026-09-07T10:00:00",
    )

    assert response.status_code == 400

def test_appointment_with_timezone_is_rejected(
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

    assert response.status_code == 422

def test_appointment_not_on_15_minute_grid(
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
        start_time="2026-09-07T10:10:00",
    )

    assert response.status_code in (400, 422)

def test_appointment_before_business_hours(
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
        start_time="2026-09-07T08:00:00",
    )

    assert response.status_code == 400

def test_appointment_after_business_hours(
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
        start_time="2026-09-07T17:00:00",
    )

    assert response.status_code == 400

def test_appointment_on_closed_day(
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

    assert response.status_code == 400

def test_appointment_when_barber_is_off(
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

    assert response.status_code == 400

# ============================================================
# CROSS-SHOP DATA ISOLATION
# ============================================================

def test_customer_from_different_shop_cannot_book(
    session,
    configured_shop,
    services,
    barbers,
):
    response = session.post(
        f"{BASE_URL}/shops",
        json={
            "name": "SECOND TEST SHOP",
            "phone": "2145558888",
            "email": "second@test.com",
            "address": "456 Second Street",
            "timezone": "America/Chicago",
        },
    )

    check(response, 200, "Create second test shop")

    second_shop_id = response.json()["id"]

    try:
        response = session.post(
            f"{BASE_URL}/shops/{second_shop_id}/customers",
            json={
                "name": "Second Shop Customer",
                "phone": "2145557777",
                "email": "secondcustomer@test.com",
            },
        )

        check(
            response,
            200,
            "Create customer in second shop",
        )

        customer_id = response.json()["id"]

        response = create_appointment(
            session=session,
            shop_id=configured_shop,
            customer_id=customer_id,
            service_id=services["service_1_id"],
            barber_id=barbers["barber_1_id"],
            start_time="2026-09-07T10:00:00",
        )

        assert response.status_code == 400

    finally:
        session.delete(
            f"{BASE_URL}/shops/{second_shop_id}"
        )

# ============================================================
# APPOINTMENT DURATION EDGE CASES
# ============================================================

def test_45_minute_service_requires_enough_remaining_time(
    session,
    scheduled_environment,
):
    env = scheduled_environment

    response = create_appointment(
        session=session,
        shop_id=env["shop_id"],
        customer_id=env["customer_1_id"],
        service_id=env["service_2_id"],
        barber_id=env["barber_1_id"],
        start_time="2026-09-07T16:30:00",
    )

    assert response.status_code == 400


def test_45_minute_service_can_start_at_415(
    session,
    scheduled_environment,
):
    env = scheduled_environment

    response = create_appointment(
        session=session,
        shop_id=env["shop_id"],
        customer_id=env["customer_1_id"],
        service_id=env["service_2_id"],
        barber_id=env["barber_1_id"],
        start_time="2026-09-07T16:15:00",
    )

    check(
        response,
        200,
        "45-minute service fits exactly until barber close",
    )

# ============================================================
# STATUS EDGE CASES
# ============================================================

def test_invalid_appointment_status(
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
        f"{BASE_URL}/shops/{env['shop_id']}/appointments/{appointment_id}/status",
        json={
            "status": "INVALID_STATUS"
        },
    )

    assert response.status_code == 400


def test_get_nonexistent_appointment(
    session,
    configured_shop,
):
    fake_appointment_id = "00000000-0000-0000-0000-000000000000"

    response = session.get(
        f"{BASE_URL}/shops/{configured_shop}/appointments/{fake_appointment_id}"
    )

    assert response.status_code == 404

# ============================================================
# MALFORMED INPUT
# ============================================================

def test_invalid_shop_uuid(session):
    response = session.get(
        f"{BASE_URL}/shops/not-a-uuid"
    )

    assert response.status_code == 422


def test_invalid_barber_uuid(session):
    response = session.get(
        f"{BASE_URL}/barbers/not-a-uuid/hours"
    )

    assert response.status_code == 422


def test_invalid_date_for_availability(
    session,
    configured_shop,
    services,
):
    response = session.get(
        f"{BASE_URL}/shops/{configured_shop}/availability",
        params={
            "service_id": services["service_1_id"],
            "date": "not-a-date",
        },
    )

    assert response.status_code == 422