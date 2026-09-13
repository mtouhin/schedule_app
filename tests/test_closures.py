from tests.helpers import BASE_URL, check


def test_create_full_day_holiday(
    session,
    configured_shop,
):
    response = session.post(
        f"{BASE_URL}/shops/{configured_shop}/closures",
        json={
            "closure_date": "2026-12-25",
            "reason": "Christmas",
            "closure_type": "HOLIDAY",
        },
    )

    check(
        response,
        200,
        "Create full-day Christmas closure",
    )

    closure = response.json()

    assert closure["start_time"] is None
    assert closure["end_time"] is None
    assert closure["reason"] == "Christmas"
    assert closure["closure_type"] == "HOLIDAY"


def test_create_partial_day_closure(
    session,
    configured_shop,
):
    response = session.post(
        f"{BASE_URL}/shops/{configured_shop}/closures",
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
        "Create partial-day holiday closure",
    )

    closure = response.json()

    assert closure["start_time"] == "09:00:00"
    assert closure["end_time"] == "13:00:00"
    assert closure["closure_type"] == "HOLIDAY"


def test_create_emergency_closure(
    session,
    configured_shop,
):
    response = session.post(
        f"{BASE_URL}/shops/{configured_shop}/closures",
        json={
            "closure_date": "2026-09-15",
            "reason": "Emergency power outage",
            "closure_type": "EMERGENCY",
        },
    )

    check(
        response,
        200,
        "Create emergency closure",
    )

    closure = response.json()

    assert closure["closure_type"] == "EMERGENCY"


def test_get_closures(
    session,
    configured_shop,
):
    session.post(
        f"{BASE_URL}/shops/{configured_shop}/closures",
        json={
            "closure_date": "2026-12-25",
            "reason": "Christmas",
            "closure_type": "HOLIDAY",
        },
    )

    session.post(
        f"{BASE_URL}/shops/{configured_shop}/closures",
        json={
            "closure_date": "2026-09-15",
            "reason": "Power outage",
            "closure_type": "EMERGENCY",
        },
    )

    response = session.get(
        f"{BASE_URL}/shops/{configured_shop}/closures"
    )

    check(
        response,
        200,
        "Get shop closures",
    )

    closures = response.json()

    assert len(closures) == 2


def test_get_individual_closure(
    session,
    configured_shop,
):
    response = session.post(
        f"{BASE_URL}/shops/{configured_shop}/closures",
        json={
            "closure_date": "2026-12-25",
            "reason": "Christmas",
            "closure_type": "HOLIDAY",
        },
    )

    check(response, 200, "Create closure")

    closure_id = response.json()["id"]

    response = session.get(
        f"{BASE_URL}/shops/{configured_shop}/closures/{closure_id}"
    )

    check(
        response,
        200,
        "Get individual closure",
    )

    closure = response.json()

    assert closure["id"] == closure_id


def test_duplicate_closure_date(
    session,
    configured_shop,
):
    payload = {
        "closure_date": "2026-12-25",
        "reason": "Christmas",
        "closure_type": "HOLIDAY",
    }

    response = session.post(
        f"{BASE_URL}/shops/{configured_shop}/closures",
        json=payload,
    )

    check(response, 200, "Create first closure")

    response = session.post(
        f"{BASE_URL}/shops/{configured_shop}/closures",
        json=payload,
    )

    check(
        response,
        409,
        "Reject duplicate closure date",
    )


def test_invalid_closure_times(
    session,
    configured_shop,
):
    response = session.post(
        f"{BASE_URL}/shops/{configured_shop}/closures",
        json={
            "closure_date": "2026-10-31",
            "start_time": "14:00:00",
            "end_time": "10:00:00",
            "reason": "Invalid closure",
            "closure_type": "HOLIDAY",
        },
    )

    check(
        response,
        422,
        "Reject closure with end before start",
    )


def test_delete_closure(
    session,
    configured_shop,
):
    response = session.post(
        f"{BASE_URL}/shops/{configured_shop}/closures",
        json={
            "closure_date": "2026-09-15",
            "reason": "Power outage",
            "closure_type": "EMERGENCY",
        },
    )

    check(response, 200, "Create emergency closure")

    closure_id = response.json()["id"]

    response = session.delete(
        f"{BASE_URL}/shops/{configured_shop}/closures/{closure_id}"
    )

    check(
        response,
        200,
        "Delete emergency closure",
    )

    response = session.get(
        f"{BASE_URL}/shops/{configured_shop}/closures/{closure_id}"
    )

    check(
        response,
        404,
        "Deleted closure no longer exists",
    )