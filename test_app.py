import requests


BASE_URL = "http://127.0.0.1:8000"


# ============================================================
# Test helpers
# ============================================================

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


# ============================================================
# Main test
# ============================================================

shop_id = None

try:

    # ========================================================
    # 1. SHOP
    # ========================================================

    print_section("1. SHOP")

    response = requests.post(
        f"{BASE_URL}/shops",
        json={
            "name": "TEST - Barber Shop",
            "phone": "2145551234",
            "email": "test@barbershop.com",
            "address": "123 Test Street, Dallas, TX",
            "timezone": "America/Chicago"
        }
    )

    check(
        response,
        200,
        "Create shop"
    )

    shop = response.json()
    shop_id = shop["id"]

    print("Shop ID:", shop_id)


    # --------------------------------------------------------
    # Get shop
    # --------------------------------------------------------

    response = requests.get(
        f"{BASE_URL}/shops/{shop_id}"
    )

    check(
        response,
        200,
        "Retrieve shop"
    )


    # --------------------------------------------------------
    # Nonexistent shop
    # --------------------------------------------------------

    response = requests.get(
        f"{BASE_URL}/shops/00000000-0000-0000-0000-000000000000"
    )

    check(
        response,
        404,
        "Reject nonexistent shop"
    )


    # ========================================================
    # 2. BUSINESS HOURS
    # ========================================================

    print_section("2. BUSINESS HOURS")


    # Monday: 9 AM - 6 PM

    response = requests.put(
        f"{BASE_URL}/shops/{shop_id}/business-hours",
        json={
            "day_of_week": 0,
            "open_time": "9:00 AM",
            "close_time": "6:00 PM",
            "is_closed": False
        }
    )

    check(
        response,
        200,
        "Set Monday business hours"
    )


    # Tuesday: 9 AM - 8 PM

    response = requests.put(
        f"{BASE_URL}/shops/{shop_id}/business-hours",
        json={
            "day_of_week": 1,
            "open_time": "9:00 AM",
            "close_time": "8:00 PM",
            "is_closed": False
        }
    )

    check(
        response,
        200,
        "Set Tuesday business hours"
    )


    # Wednesday closed

    response = requests.put(
        f"{BASE_URL}/shops/{shop_id}/business-hours",
        json={
            "day_of_week": 2,
            "open_time": None,
            "close_time": None,
            "is_closed": True
        }
    )

    check(
        response,
        200,
        "Set Wednesday as closed"
    )


    # --------------------------------------------------------
    # Business hours edge cases
    # --------------------------------------------------------

    print("\n--- Business hours edge cases ---")


    # Before 5 AM

    response = requests.put(
        f"{BASE_URL}/shops/{shop_id}/business-hours",
        json={
            "day_of_week": 3,
            "open_time": "4:00 AM",
            "close_time": "6:00 PM",
            "is_closed": False
        }
    )

    check(
        response,
        422,
        "Reject opening before 5 AM"
    )


    # Not a 15-minute increment

    response = requests.put(
        f"{BASE_URL}/shops/{shop_id}/business-hours",
        json={
            "day_of_week": 3,
            "open_time": "9:10 AM",
            "close_time": "6:00 PM",
            "is_closed": False
        }
    )

    check(
        response,
        422,
        "Reject non-15-minute opening time"
    )


    # Closing after allowed time

    response = requests.put(
        f"{BASE_URL}/shops/{shop_id}/business-hours",
        json={
            "day_of_week": 3,
            "open_time": "9:00 AM",
            "close_time": "11:50 PM",
            "is_closed": False
        }
    )

    check(
        response,
        422,
        "Reject closing after 11:45 PM"
    )


    # Close before open

    response = requests.put(
        f"{BASE_URL}/shops/{shop_id}/business-hours",
        json={
            "day_of_week": 4,
            "open_time": "6:00 PM",
            "close_time": "9:00 AM",
            "is_closed": False
        }
    )

    check(
        response,
        400,
        "Reject close before open"
    )


    # Missing times

    response = requests.put(
        f"{BASE_URL}/shops/{shop_id}/business-hours",
        json={
            "day_of_week": 4,
            "open_time": None,
            "close_time": None,
            "is_closed": False
        }
    )

    check(
        response,
        400,
        "Reject missing hours when shop is open"
    )


    # --------------------------------------------------------
    # Retrieve hours
    # --------------------------------------------------------

    response = requests.get(
        f"{BASE_URL}/shops/{shop_id}/business-hours"
    )

    check(
        response,
        200,
        "Retrieve business hours"
    )


    # ========================================================
    # 3. BARBERS
    # ========================================================

    print_section("3. BARBERS")


    # Barber 1

    response = requests.post(
        f"{BASE_URL}/shops/{shop_id}/barbers",
        json={
            "name": "John",
            "phone": "2145551111",
            "email": "john@test.com"
        }
    )

    check(
        response,
        200,
        "Create John"
    )

    barber_1 = response.json()
    barber_1_id = barber_1["id"]


    # Barber 2

    response = requests.post(
        f"{BASE_URL}/shops/{shop_id}/barbers",
        json={
            "name": "Mike",
            "phone": "2145552222",
            "email": "mike@test.com"
        }
    )

    check(
        response,
        200,
        "Create Mike"
    )

    barber_2 = response.json()
    barber_2_id = barber_2["id"]


    # --------------------------------------------------------
    # Duplicate barber name
    # --------------------------------------------------------

    response = requests.post(
        f"{BASE_URL}/shops/{shop_id}/barbers",
        json={
            "name": "John",
            "phone": "2145553333",
            "email": "another@test.com"
        }
    )

    check(
        response,
        409,
        "Reject duplicate barber name"
    )


    # --------------------------------------------------------
    # Duplicate phone
    # --------------------------------------------------------

    response = requests.post(
        f"{BASE_URL}/shops/{shop_id}/barbers",
        json={
            "name": "Another Barber",
            "phone": "2145551111",
            "email": "another@test.com"
        }
    )

    check(
        response,
        409,
        "Reject duplicate barber phone"
    )


    # --------------------------------------------------------
    # Duplicate email
    # --------------------------------------------------------

    response = requests.post(
        f"{BASE_URL}/shops/{shop_id}/barbers",
        json={
            "name": "Another Barber",
            "phone": "2145554444",
            "email": "JOHN@TEST.COM"
        }
    )

    check(
        response,
        409,
        "Reject duplicate barber email"
    )


    # --------------------------------------------------------
    # Get barbers
    # --------------------------------------------------------

    response = requests.get(
        f"{BASE_URL}/shops/{shop_id}/barbers"
    )

    check(
        response,
        200,
        "Retrieve barbers"
    )


    # ========================================================
    # 4. BARBER HOURS
    # ========================================================

    print_section("4. BARBER HOURS")


    # John: 9 AM - 5 PM

    response = requests.put(
        f"{BASE_URL}/barbers/{barber_1_id}/hours",
        json={
            "day_of_week": 0,
            "start_time": "9:00 AM",
            "end_time": "5:00 PM",
            "is_off": False
        }
    )

    check(
        response,
        200,
        "Set John's Monday hours"
    )


    # Mike: 10 AM - 6 PM

    response = requests.put(
        f"{BASE_URL}/barbers/{barber_2_id}/hours",
        json={
            "day_of_week": 0,
            "start_time": "10:00 AM",
            "end_time": "6:00 PM",
            "is_off": False
        }
    )

    check(
        response,
        200,
        "Set Mike's Monday hours"
    )


    # --------------------------------------------------------
    # Barber starts before shop
    # --------------------------------------------------------

    response = requests.put(
        f"{BASE_URL}/barbers/{barber_1_id}/hours",
        json={
            "day_of_week": 0,
            "start_time": "8:00 AM",
            "end_time": "5:00 PM",
            "is_off": False
        }
    )

    check(
        response,
        400,
        "Reject barber starting before shop opens"
    )


    # --------------------------------------------------------
    # Barber ends after shop
    # --------------------------------------------------------

    response = requests.put(
        f"{BASE_URL}/barbers/{barber_1_id}/hours",
        json={
            "day_of_week": 0,
            "start_time": "9:00 AM",
            "end_time": "7:00 PM",
            "is_off": False
        }
    )

    check(
        response,
        400,
        "Reject barber ending after shop closes"
    )


    # --------------------------------------------------------
    # Barber works on closed day
    # --------------------------------------------------------

    response = requests.put(
        f"{BASE_URL}/barbers/{barber_1_id}/hours",
        json={
            "day_of_week": 2,
            "start_time": "9:00 AM",
            "end_time": "5:00 PM",
            "is_off": False
        }
    )

    check(
        response,
        400,
        "Reject barber working on shop closed day"
    )


    # --------------------------------------------------------
    # Barber day off
    # --------------------------------------------------------

    response = requests.put(
        f"{BASE_URL}/barbers/{barber_1_id}/hours",
        json={
            "day_of_week": 2,
            "start_time": None,
            "end_time": None,
            "is_off": True
        }
    )

    check(
        response,
        200,
        "Allow barber day off"
    )


    # --------------------------------------------------------
    # Invalid 15-minute increment
    # --------------------------------------------------------

    response = requests.put(
        f"{BASE_URL}/barbers/{barber_1_id}/hours",
        json={
            "day_of_week": 0,
            "start_time": "9:10 AM",
            "end_time": "5:00 PM",
            "is_off": False
        }
    )

    check(
        response,
        422,
        "Reject barber non-15-minute start"
    )


    # ========================================================
    # 5. SERVICES
    # ========================================================

    print_section("5. SERVICES")


    # Haircut

    response = requests.post(
        f"{BASE_URL}/shops/{shop_id}/services",
        json={
            "name": "Haircut",
            "description": "Standard haircut",
            "duration_minutes": 30,
            "price_cents": 3000
        }
    )

    check(
        response,
        200,
        "Create haircut service"
    )

    service_1 = response.json()
    service_1_id = service_1["id"]


    # Haircut + Beard

    response = requests.post(
        f"{BASE_URL}/shops/{shop_id}/services",
        json={
            "name": "Haircut + Beard",
            "description": "Haircut and beard trim",
            "duration_minutes": 45,
            "price_cents": 4500
        }
    )

    check(
        response,
        200,
        "Create haircut + beard service"
    )

    service_2 = response.json()
    service_2_id = service_2["id"]


    # --------------------------------------------------------
    # Get services
    # --------------------------------------------------------

    response = requests.get(
        f"{BASE_URL}/shops/{shop_id}/services"
    )

    check(
        response,
        200,
        "Retrieve services"
    )


    # ========================================================
    # 6. CUSTOMERS
    # ========================================================

    print_section("6. CUSTOMERS")


    # Alice

    response = requests.post(
        f"{BASE_URL}/shops/{shop_id}/customers",
        json={
            "name": "Alice",
            "phone": "2145555001",
            "email": "alice@test.com"
        }
    )

    check(
        response,
        200,
        "Create Alice"
    )

    customer_1 = response.json()
    customer_1_id = customer_1["id"]


    # Bob

    response = requests.post(
        f"{BASE_URL}/shops/{shop_id}/customers",
        json={
            "name": "Bob",
            "phone": "2145555002",
            "email": "bob@test.com"
        }
    )

    check(
        response,
        200,
        "Create Bob"
    )

    customer_2 = response.json()
    customer_2_id = customer_2["id"]


    # --------------------------------------------------------
    # Duplicate customer
    # --------------------------------------------------------

    response = requests.post(
        f"{BASE_URL}/shops/{shop_id}/customers",
        json={
            "name": "Alice Again",
            "phone": "2145555001",
            "email": "different@test.com"
        }
    )

    check(
        response,
        409,
        "Reject duplicate customer phone"
    )


    # --------------------------------------------------------
    # Get customer
    # --------------------------------------------------------

    response = requests.get(
        f"{BASE_URL}/shops/{shop_id}/customers/phone/2145555001"
    )

    check(
        response,
        200,
        "Retrieve customer by phone"
    )


    # ========================================================
    # 7. AVAILABILITY
    # ========================================================

    print_section("7. AVAILABILITY")


    # Monday = September 7, 2026
    #
    # John:
    # 9 AM - 5 PM
    #
    # Mike:
    # 10 AM - 6 PM
    #
    # Haircut:
    # 30 minutes

    response = requests.get(
        f"{BASE_URL}/shops/{shop_id}/availability",
        params={
            "service_id": service_1_id,
            "date": "2026-09-07"
        }
    )

    check(
        response,
        200,
        "Get availability"
    )

    availability = response.json()

    print("\nAvailable times:")

    for slot in availability["available_times"]:
        print(slot)


    # --------------------------------------------------------
    # John's availability
    # --------------------------------------------------------

    response = requests.get(
        f"{BASE_URL}/shops/{shop_id}/availability",
        params={
            "service_id": service_1_id,
            "date": "2026-09-07",
            "barber_id": barber_1_id
        }
    )

    check(
        response,
        200,
        "Get John's availability"
    )


    # --------------------------------------------------------
    # Closed day
    # --------------------------------------------------------

    response = requests.get(
        f"{BASE_URL}/shops/{shop_id}/availability",
        params={
            "service_id": service_1_id,
            "date": "2026-09-09"
        }
    )

    check(
        response,
        200,
        "Check closed-day availability"
    )

    closed_day = response.json()

    assert closed_day["available_times"] == []

    print("PASSED: Closed day has no available times")


    # ========================================================
    # 8. CREATE APPOINTMENT
    # ========================================================

    print_section("8. APPOINTMENTS")


    # Alice → John → 10 AM

    response = requests.post(
        f"{BASE_URL}/shops/{shop_id}/appointments",
        json={
            "customer_id": customer_1_id,
            "service_id": service_1_id,
            "barber_id": barber_1_id,
            "start_time": "2026-09-07T10:00:00",
            "notes": "Test appointment"
        }
    )

    check(
        response,
        200,
        "Create appointment"
    )

    appointment_1 = response.json()
    appointment_1_id = appointment_1["id"]

    print("Appointment ID:", appointment_1_id)


    # ========================================================
    # 9. DOUBLE BOOKING
    # ========================================================

    print_section("9. DOUBLE BOOKING")


    # Bob tries John at same time

    response = requests.post(
        f"{BASE_URL}/shops/{shop_id}/appointments",
        json={
            "customer_id": customer_2_id,
            "service_id": service_1_id,
            "barber_id": barber_1_id,
            "start_time": "2026-09-07T10:00:00",
            "notes": "Should fail"
        }
    )

    check(
        response,
        400,
        "Reject double booking"
    )


    # ========================================================
    # 10. BACK-TO-BACK
    # ========================================================

    print_section("10. BACK-TO-BACK APPOINTMENT")


    # Existing:
    #
    # 10:00 - 10:30
    #
    # This should work:
    #
    # 10:30 - 11:00

    response = requests.post(
        f"{BASE_URL}/shops/{shop_id}/appointments",
        json={
            "customer_id": customer_2_id,
            "service_id": service_1_id,
            "barber_id": barber_1_id,
            "start_time": "2026-09-07T10:30:00",
            "notes": "Back-to-back"
        }
    )

    check(
        response,
        200,
        "Allow back-to-back appointment"
    )


    # ========================================================
    # 11. OVERLAPPING APPOINTMENT
    # ========================================================

    print_section("11. OVERLAPPING APPOINTMENT")


    # Existing:
    #
    # 10:30 - 11:00
    #
    # Try:
    #
    # 10:15 - 10:45
    #
    # Should fail.

    response = requests.post(
        f"{BASE_URL}/shops/{shop_id}/appointments",
        json={
            "customer_id": customer_2_id,
            "service_id": service_1_id,
            "barber_id": barber_1_id,
            "start_time": "2026-09-07T10:15:00",
            "notes": "Should fail"
        }
    )

    check(
        response,
        400,
        "Reject overlapping appointment"
    )


    # ========================================================
    # 12. ANY BARBER
    # ========================================================

    print_section("12. ANY BARBER")


    # John and Mike both exist.
    #
    # At 11 AM there should be availability.
    #
    # barber_id = None means:
    #
    # "I don't care who cuts my hair."

    response = requests.post(
        f"{BASE_URL}/shops/{shop_id}/appointments",
        json={
            "customer_id": customer_2_id,
            "service_id": service_1_id,
            "barber_id": None,
            "start_time": "2026-09-07T11:00:00",
            "notes": "Any barber"
        }
    )

    check(
        response,
        200,
        "Book with any available barber"
    )

    any_barber = response.json()

    print(
        "Assigned barber:",
        any_barber["barber_id"]
    )


    # ========================================================
    # 13. SERVICE DELETION
    # ========================================================

    print_section("13. SERVICE DELETION")


    # service_1 has appointments.
    #
    # Therefore it should NOT be physically deleted.

    response = requests.delete(
        f"{BASE_URL}/shops/{shop_id}/services/{service_1_id}"
    )

    check(
        response,
        409,
        "Prevent deleting service with appointments"
    )


    # service_2 has NO appointments.
    #
    # This one can be deleted.

    response = requests.delete(
        f"{BASE_URL}/shops/{shop_id}/services/{service_2_id}"
    )

    check(
        response,
        200,
        "Delete unused service"
    )


    # ========================================================
    # 14. SHOP DELETION
    # ========================================================

    print_section("14. SHOP DELETION")


    response = requests.delete(
        f"{BASE_URL}/shops/{shop_id}"
    )

    check(
        response,
        200,
        "Delete test shop"
    )

    # Important:
    #
    # Set to None so the finally block
    # does not try to delete it again.

    shop_id = None


    # ========================================================
    # SUCCESS
    # ========================================================

    print_section("ALL TESTS PASSED")

    print(
        "The complete barber booking flow passed."
    )


finally:

    # ========================================================
    # CLEANUP
    # ========================================================

    print_section("CLEANUP")

    if shop_id:

        print(
            "Tests stopped before normal cleanup."
        )

        print(
            f"Deleting test shop: {shop_id}"
        )

        response = requests.delete(
            f"{BASE_URL}/shops/{shop_id}"
        )

        if response.status_code in [200, 204, 404]:

            print(
                "Test data successfully cleaned up."
            )

        else:

            print(
                "WARNING: Could not clean up test shop."
            )

            print(
                response.text
            )

    else:

        print(
            "No cleanup necessary."
        )