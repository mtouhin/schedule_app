import requests


BASE_URL = "http://127.0.0.1:8000"


def check(response, expected_status, description):
    print(f"\nTEST: {description}")
    print(f"Expected: {expected_status}")
    print(f"Actual:   {response.status_code}")

    if response.status_code != expected_status:
        print("\nResponse:")
        print(response.text)

        raise AssertionError(
            f"FAILED: {description}"
        )

    print("PASSED")


def print_section(title):
    print("\n")
    print("=" * 60)
    print(title)
    print("=" * 60)


def create_shop(session):
    response = session.post(
        f"{BASE_URL}/shops",
        json={
            "name": "TEST - Barber Shop",
            "phone": "2145551234",
            "email": "test@barbershop.com",
            "address": "123 Test Street, Dallas, TX",
            "timezone": "America/Chicago",
        },
    )

    check(response, 200, "Create test shop")

    return response.json()


def set_business_hours(session, shop_id):
    hours = [
        {
            "day_of_week": 0,
            "open_time": "9:00 AM",
            "close_time": "6:00 PM",
            "is_closed": False,
        },
        {
            "day_of_week": 1,
            "open_time": "9:00 AM",
            "close_time": "8:00 PM",
            "is_closed": False,
        },
        {
            "day_of_week": 2,
            "open_time": None,
            "close_time": None,
            "is_closed": True,
        },
        {
            "day_of_week": 3,
            "open_time": "9:00 AM",
            "close_time": "6:00 PM",
            "is_closed": False,
        },
        {
            "day_of_week": 4,
            "open_time": "9:00 AM",
            "close_time": "6:00 PM",
            "is_closed": False,
        },
    ]

    for day in hours:
        response = session.put(
            f"{BASE_URL}/shops/{shop_id}/business-hours",
            json=day,
        )

        check(
            response,
            200,
            f"Set business hours for day {day['day_of_week']}",
        )


def create_barbers(session, shop_id):
    response = session.post(
        f"{BASE_URL}/shops/{shop_id}/barbers",
        json={
            "name": "John",
            "phone": "2145551111",
            "email": "john@test.com",
        },
    )

    check(response, 200, "Create John")

    barber_1 = response.json()

    response = session.post(
        f"{BASE_URL}/shops/{shop_id}/barbers",
        json={
            "name": "Mike",
            "phone": "2145552222",
            "email": "mike@test.com",
        },
    )

    check(response, 200, "Create Mike")

    barber_2 = response.json()

    return {
        "barber_1": barber_1,
        "barber_2": barber_2,
        "barber_1_id": barber_1["id"],
        "barber_2_id": barber_2["id"],
    }


def set_barber_hours(session, barber_1_id, barber_2_id):
    # John works Monday 9 AM - 5 PM
    response = session.put(
        f"{BASE_URL}/barbers/{barber_1_id}/hours",
        json={
            "day_of_week": 0,
            "start_time": "9:00 AM",
            "end_time": "5:00 PM",
            "is_off": False,
        },
    )

    check(response, 200, "Set John's Monday hours")

    # Mike works Monday 10 AM - 6 PM
    response = session.put(
        f"{BASE_URL}/barbers/{barber_2_id}/hours",
        json={
            "day_of_week": 0,
            "start_time": "10:00 AM",
            "end_time": "6:00 PM",
            "is_off": False,
        },
    )

    check(response, 200, "Set Mike's Monday hours")

    # John works Tuesday 9 AM - 5 PM
    response = session.put(
        f"{BASE_URL}/barbers/{barber_1_id}/hours",
        json={
            "day_of_week": 1,
            "start_time": "9:00 AM",
            "end_time": "5:00 PM",
            "is_off": False,
        },
    )

    check(response, 200, "Set John's Tuesday hours")

    # John is OFF Wednesday
    response = session.put(
        f"{BASE_URL}/barbers/{barber_1_id}/hours",
        json={
            "day_of_week": 2,
            "is_off": True,
        },
    )

    check(response, 200, "Set John's Wednesday off day")

    # Mike works Tuesday 10 AM - 6 PM
    response = session.put(
        f"{BASE_URL}/barbers/{barber_2_id}/hours",
        json={
            "day_of_week": 1,
            "start_time": "10:00 AM",
            "end_time": "6:00 PM",
            "is_off": False,
        },
    )

    check(response, 200, "Set Mike's Tuesday hours")

    # John works Thursday 9 AM - 5 PM.
    # Thursday is useful for the closure-availability tests.
    response = session.put(
        f"{BASE_URL}/barbers/{barber_1_id}/hours",
        json={
            "day_of_week": 3,
            "start_time": "9:00 AM",
            "end_time": "5:00 PM",
            "is_off": False,
        },
    )

    check(response, 200, "Set John's Thursday hours")

    # Mike works Thursday 10 AM - 6 PM.
    response = session.put(
        f"{BASE_URL}/barbers/{barber_2_id}/hours",
        json={
            "day_of_week": 3,
            "start_time": "10:00 AM",
            "end_time": "6:00 PM",
            "is_off": False,
        },
    )

    check(response, 200, "Set Mike's Thursday hours")

    # John works Friday 9 AM - 5 PM.
    response = session.put(
        f"{BASE_URL}/barbers/{barber_1_id}/hours",
        json={
            "day_of_week": 4,
            "start_time": "9:00 AM",
            "end_time": "5:00 PM",
            "is_off": False,
        },
    )

    check(response, 200, "Set John's Friday off day")

    # Mike works Friday 10 AM - 6 PM.
    response = session.put(
        f"{BASE_URL}/barbers/{barber_2_id}/hours",
        json={
            "day_of_week": 4,
            "start_time": "10:00 AM",
            "end_time": "6:00 PM",
            "is_off": False,
        },
    )

    check(response, 200, "Set Mike's Friday hours")


def create_services(session, shop_id):
    response = session.post(
        f"{BASE_URL}/shops/{shop_id}/services",
        json={
            "name": "Haircut",
            "description": "Standard haircut",
            "duration_minutes": 30,
            "price_cents": 3000,
        },
    )

    check(response, 200, "Create haircut service")

    service_1 = response.json()

    response = session.post(
        f"{BASE_URL}/shops/{shop_id}/services",
        json={
            "name": "Haircut + Beard",
            "description": "Haircut and beard trim",
            "duration_minutes": 45,
            "price_cents": 4500,
        },
    )

    check(response, 200, "Create haircut + beard service")

    service_2 = response.json()

    return {
        "service_1": service_1,
        "service_2": service_2,
        "service_1_id": service_1["id"],
        "service_2_id": service_2["id"],
    }


def create_customers(session, shop_id):
    response = session.post(
        f"{BASE_URL}/shops/{shop_id}/customers",
        json={
            "name": "Alice",
            "phone": "2145555001",
            "email": "alice@test.com",
        },
    )

    check(response, 200, "Create Alice")

    customer_1 = response.json()

    response = session.post(
        f"{BASE_URL}/shops/{shop_id}/customers",
        json={
            "name": "Bob",
            "phone": "2145555002",
            "email": "bob@test.com",
        },
    )

    check(response, 200, "Create Bob")

    customer_2 = response.json()

    return {
        "customer_1": customer_1,
        "customer_2": customer_2,
        "customer_1_id": customer_1["id"],
        "customer_2_id": customer_2["id"],
    }


def get_availability(
    session,
    shop_id,
    service_id,
    selected_date,
    barber_id=None,
):
    params = {
        "service_id": service_id,
        "date": selected_date,
    }

    if barber_id is not None:
        params["barber_id"] = barber_id

    return session.get(
        f"{BASE_URL}/shops/{shop_id}/availability",
        params=params,
    )


def create_appointment(
    session,
    shop_id,
    customer_id,
    service_id,
    start_time,
    barber_id=None,
    notes=None,
):
    return session.post(
        f"{BASE_URL}/shops/{shop_id}/appointments",
        json={
            "customer_id": customer_id,
            "service_id": service_id,
            "barber_id": barber_id,
            "start_time": start_time,
            "notes": notes,
        },
    )