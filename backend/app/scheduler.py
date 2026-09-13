from datetime import datetime, date, time, timedelta
from uuid import UUID
from typing import Optional
from psycopg.rows import dict_row
from app.db import get_connection

SLOT_MINUTES = 15

def make_time_naive(value):
    if value is None:
        return None

    return time(
        value.hour,
        value.minute,
        value.second,
        value.microsecond
    )

def get_day_of_week(selected_date: date) -> int:
    """
    Python:
        Monday = 0
        Sunday = 6

    This matches our database design.
    """
    return selected_date.weekday()

def get_service_duration(shop_id: UUID, service_id: UUID):
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT duration_minutes
                FROM services
                WHERE id = %s
                  AND shop_id = %s
                  AND is_active = TRUE;
                """,
                (service_id, shop_id)
            )

            service = cursor.fetchone()

            if not service:
                raise ValueError("Service not found")

            return service["duration_minutes"]

def get_barber_hours(barber_id: UUID, day_of_week: int):
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT
                    start_time,
                    end_time,
                    is_off
                FROM barber_hours
                WHERE barber_id = %s
                  AND day_of_week = %s;
                """,
                (barber_id, day_of_week)
            )

            return cursor.fetchone()

def get_business_hours(shop_id: UUID, day_of_week: int):
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT
                    open_time,
                    close_time,
                    is_closed
                FROM business_hours
                WHERE shop_id = %s
                  AND day_of_week = %s;
                """,
                (shop_id, day_of_week)
            )

            return cursor.fetchone()

def get_shop_exception(shop_id: UUID, selected_date: date):
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    closure_date,
                    start_time,
                    end_time,
                    reason,
                    closure_type
                FROM shop_closures
                WHERE shop_id = %s
                  AND closure_date = %s;
                """,
                (shop_id, selected_date)
            )

            return cursor.fetchone()

def get_barber_appointments(
    barber_id: UUID,
    selected_date: date
):
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT
                    start_time,
                    end_time
                FROM appointments
                WHERE barber_id = %s
                  AND DATE(start_time) = %s
                  AND status NOT IN ('CANCELLED', 'NO_SHOW')
                ORDER BY start_time;
                """,
                (barber_id, selected_date)
            )

            return cursor.fetchall()

def get_active_barbers(shop_id: UUID):
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    name
                FROM barbers
                WHERE shop_id = %s
                  AND is_active = TRUE
                ORDER BY name;
                """,
                (shop_id,)
            )

            return cursor.fetchall()

def overlaps(
    start_time: datetime,
    end_time: datetime,
    appointments
):
    for appointment in appointments:
        existing_start = appointment["start_time"]
        existing_end = appointment["end_time"]

        if start_time < existing_end and end_time > existing_start:
            return True

    return False


def generate_slots(
    start_time: time,
    end_time: time,
    duration_minutes: int
):
    slots = []

    current = datetime.combine(date.today(), start_time)
    closing = datetime.combine(date.today(), end_time)

    while current + timedelta(minutes=duration_minutes) <= closing:
        slots.append(current.time())

        current += timedelta(minutes=15)

    return slots

def get_available_times(
    shop_id: UUID,
    service_id: UUID,
    selected_date: date,
    barber_id: Optional[UUID] = None
):
    day_of_week = get_day_of_week(selected_date)

    # ---------------------------------------------------------
    # 1. Verify service
    # ---------------------------------------------------------

    duration_minutes = get_service_duration(
        shop_id,
        service_id
    )

    # ---------------------------------------------------------
    # 2. Get normal business hours
    # ---------------------------------------------------------

    business_hours = get_business_hours(
        shop_id,
        day_of_week
    )

    if not business_hours:
        return []

    if business_hours["is_closed"]:
        return []

    shop_open = make_time_naive(
        business_hours["open_time"]
    )

    shop_close = make_time_naive(
        business_hours["close_time"]
    )

    if shop_open is None or shop_close is None:
        return []

    # ---------------------------------------------------------
    # 3. Check for a date-specific shop exception
    # ---------------------------------------------------------

    shop_exception = get_shop_exception(
        shop_id,
        selected_date
    )

    if shop_exception:

        exception_start = make_time_naive(
            shop_exception["start_time"]
        )

        exception_end = make_time_naive(
            shop_exception["end_time"]
        )

        # Both NULL = completely closed
        if exception_start is None and exception_end is None:
            return []

        # One NULL but not the other = invalid data
        if exception_start is None or exception_end is None:
            return []

        # Special hours override normal business hours
        shop_open = exception_start
        shop_close = exception_end

    # ---------------------------------------------------------
    # 4. Determine which barbers to check
    # ---------------------------------------------------------

    if barber_id is not None:

        with get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    """
                    SELECT
                        id,
                        shop_id,
                        is_active
                    FROM barbers
                    WHERE id = %s
                      AND shop_id = %s;
                    """,
                    (barber_id, shop_id)
                )

                barber = cursor.fetchone()

        if not barber:
            raise ValueError("Barber not found")

        if not barber["is_active"]:
            return []

        barbers = [barber]

    else:
        barbers = get_active_barbers(shop_id)

    # No active barbers
    if not barbers:
        return []

    # ---------------------------------------------------------
    # 5. Find available slots for each barber
    # ---------------------------------------------------------

    results = []

    for barber in barbers:

        barber_hours = get_barber_hours(
            barber["id"],
            day_of_week
        )

        if not barber_hours:
            continue

        if barber_hours["is_off"]:
            continue

        barber_start = make_time_naive(
            barber_hours["start_time"]
        )

        barber_end = make_time_naive(
            barber_hours["end_time"]
        )

        if barber_start is None or barber_end is None:
            continue

        # -----------------------------------------------------
        # Barber must operate inside shop hours
        # -----------------------------------------------------

        effective_start = max(
            shop_open,
            barber_start
        )

        effective_end = min(
            shop_close,
            barber_end
        )

        if effective_start >= effective_end:
            continue

        # -----------------------------------------------------
        # Generate 15-minute slots
        # -----------------------------------------------------

        slots = generate_slots(
            effective_start,
            effective_end,
            duration_minutes
        )

        # -----------------------------------------------------
        # Existing appointments
        # -----------------------------------------------------

        appointments = get_barber_appointments(
            barber["id"],
            selected_date
        )

        for slot in slots:

            slot_start = datetime.combine(
                selected_date,
                slot
            )

            slot_end = slot_start + timedelta(
                minutes=duration_minutes
            )

            # Skip occupied slots
            if overlaps(
                slot_start,
                slot_end,
                appointments
            ):
                continue

            # -------------------------------------------------
            # Specific barber
            # -------------------------------------------------

            if barber_id is not None:

                results.append(
                    {
                        "time": slot,
                        "barber_id": barber["id"]
                    }
                )

            # -------------------------------------------------
            # Anyone available
            # -------------------------------------------------

            else:

                existing_result = next(
                    (
                        result
                        for result in results
                        if result["time"] == slot
                    ),
                    None
                )

                if existing_result:
                    existing_result["barber_ids"].append(
                        barber["id"]
                    )
                else:
                    results.append(
                        {
                            "time": slot,
                            "barber_ids": [
                                barber["id"]
                            ]
                        }
                    )

    # ---------------------------------------------------------
    # Sort slots chronologically
    # ---------------------------------------------------------

    results.sort(
        key=lambda result: result["time"]
    )

    return results