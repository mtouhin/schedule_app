from tests.helpers import BASE_URL, check


def test_set_and_get_business_hours(
    session,
    configured_shop,
):
    shop_id = configured_shop

    response = session.get(
        f"{BASE_URL}/shops/{shop_id}/business-hours"
    )

    check(
        response,
        200,
        "Retrieve business hours",
    )

    hours = response.json()

    assert len(hours) >= 5


def test_reject_opening_before_5_am(
    session,
    configured_shop,
):
    response = session.put(
        f"{BASE_URL}/shops/{configured_shop}/business-hours",
        json={
            "day_of_week": 5,
            "open_time": "4:00 AM",
            "close_time": "6:00 PM",
            "is_closed": False,
        },
    )

    check(
        response,
        422,
        "Reject opening before 5 AM",
    )


def test_reject_non_15_minute_time(
    session,
    configured_shop,
):
    response = session.put(
        f"{BASE_URL}/shops/{configured_shop}/business-hours",
        json={
            "day_of_week": 5,
            "open_time": "9:10 AM",
            "close_time": "6:00 PM",
            "is_closed": False,
        },
    )

    check(
        response,
        422,
        "Reject non-15-minute opening time",
    )


def test_reject_closing_after_1145_pm(
    session,
    configured_shop,
):
    response = session.put(
        f"{BASE_URL}/shops/{configured_shop}/business-hours",
        json={
            "day_of_week": 5,
            "open_time": "9:00 AM",
            "close_time": "11:50 PM",
            "is_closed": False,
        },
    )

    check(
        response,
        422,
        "Reject closing after 11:45 PM",
    )


def test_reject_close_before_open(
    session,
    configured_shop,
):
    response = session.put(
        f"{BASE_URL}/shops/{configured_shop}/business-hours",
        json={
            "day_of_week": 5,
            "open_time": "6:00 PM",
            "close_time": "9:00 AM",
            "is_closed": False,
        },
    )

    check(
        response,
        400,
        "Reject close before open",
    )


def test_reject_missing_hours_when_open(
    session,
    configured_shop,
):
    response = session.put(
        f"{BASE_URL}/shops/{configured_shop}/business-hours",
        json={
            "day_of_week": 5,
            "open_time": None,
            "close_time": None,
            "is_closed": False,
        },
    )

    check(
        response,
        400,
        "Reject missing hours when shop is open",
    )


def test_closed_day(
    session,
    configured_shop,
):
    response = session.put(
        f"{BASE_URL}/shops/{configured_shop}/business-hours",
        json={
            "day_of_week": 6,
            "open_time": None,
            "close_time": None,
            "is_closed": True,
        },
    )

    check(
        response,
        200,
        "Allow closed day",
    )

def test_get_barber_hours(
    session,
    configured_barbers,
):
    barber_id = configured_barbers["barber_1_id"]

    response = session.get(
        f"{BASE_URL}/barbers/{barber_id}/hours"
    )

    check(
        response,
        200,
        "Retrieve barber hours",
    )


def test_barber_starts_before_shop(
    session,
    configured_shop,
    barbers,
):
    barber_id = barbers["barber_1_id"]

    response = session.put(
        f"{BASE_URL}/barbers/{barber_id}/hours",
        json={
            "day_of_week": 0,
            "start_time": "8:00 AM",
            "end_time": "5:00 PM",
            "is_off": False,
        },
    )

    check(
        response,
        400,
        "Reject barber starting before shop opens",
    )


def test_barber_ends_after_shop(
    session,
    configured_shop,
    barbers,
):
    barber_id = barbers["barber_1_id"]

    response = session.put(
        f"{BASE_URL}/barbers/{barber_id}/hours",
        json={
            "day_of_week": 0,
            "start_time": "9:00 AM",
            "end_time": "7:00 PM",
            "is_off": False,
        },
    )

    check(
        response,
        400,
        "Reject barber ending after shop closes",
    )


def test_barber_cannot_work_on_closed_day(
    session,
    configured_shop,
    barbers,
):
    barber_id = barbers["barber_1_id"]

    response = session.put(
        f"{BASE_URL}/barbers/{barber_id}/hours",
        json={
            "day_of_week": 2,
            "start_time": "9:00 AM",
            "end_time": "5:00 PM",
            "is_off": False,
        },
    )

    check(
        response,
        400,
        "Reject barber working on shop closed day",
    )


def test_barber_day_off(
    session,
    configured_shop,
    barbers,
):
    barber_id = barbers["barber_1_id"]

    response = session.put(
        f"{BASE_URL}/barbers/{barber_id}/hours",
        json={
            "day_of_week": 2,
            "start_time": None,
            "end_time": None,
            "is_off": True,
        },
    )

    check(
        response,
        200,
        "Allow barber day off",
    )


def test_barber_non_15_minute_time(
    session,
    configured_shop,
    barbers,
):
    barber_id = barbers["barber_1_id"]

    response = session.put(
        f"{BASE_URL}/barbers/{barber_id}/hours",
        json={
            "day_of_week": 0,
            "start_time": "9:10 AM",
            "end_time": "5:00 PM",
            "is_off": False,
        },
    )

    check(
        response,
        422,
        "Reject barber non-15-minute start",
    )