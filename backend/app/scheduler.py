from datetime import datetime, date, time, timedelta
from uuid import UUID

from app.db import get_connection

SLOT_MINUTES = 15

def get_day_of_week(selected_date: date) -> int:
    """
    Python:
        Monday = 0
        Sunday = 6

    This matches our database design.
    """
    return selected_date.weekday()

def get_service_duration(
    cursor,
    shop_id: UUID,
    service_id: UUID
):
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
    result = cursor.fetchone()
    if not result:
        raise ValueError("Service not found")

    return result[0]

def get_barber_hours(
    cursor,
    barber_id: UUID,
    day_of_week: int
):
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
        (
            barber_id,
            day_of_week
        )
    )
    return cursor.fetchone()

def get_business_hours(
    cursor,
    shop_id: UUID,
    day_of_week: int
):
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
        (
            shop_id,
            day_of_week
        )
    )
    return cursor.fetchone()

def is_shop_closed(
    cursor,
    shop_id: UUID,
    selected_date: date
):
    cursor.execute(
        """
        SELECT 1
        FROM shop_closures
        WHERE shop_id = %s
          AND closure_date = %s;
        """,
        (
            shop_id,
            selected_date
        )
    )
    return cursor.fetchone() is not None

def get_barber_appointments(
    cursor,
    barber_id: UUID,
    selected_date: date
):
    """
    Get all appointments for this barber on this date.
    """

    start_of_day = datetime.combine(
        selected_date,
        time.min
    )

    end_of_day = start_of_day + timedelta(days=1)

    cursor.execute(
        """
        SELECT
            start_time,
            end_time
        FROM appointments
        WHERE barber_id = %s
          AND start_time < %s
          AND end_time > %s
          AND status NOT IN (
              'CANCELLED',
              'NO_SHOW'
          )
        ORDER BY start_time;
        """,
        (
            barber_id,
            end_of_day,
            start_of_day
        )
    )

    return cursor.fetchall()

def overlaps(
    start_time: datetime,
    end_time: datetime,
    existing_start: datetime,
    existing_end: datetime
):
    """
    Returns True if two appointments overlap.
    """

    return (
        start_time < existing_end
        and
        end_time > existing_start
    )

def generate_slots(
    start_time: time,
    end_time: time,
    duration_minutes: int
):
    """
    Generate possible 15-minute appointment start times.

    Example:

    8:00 AM - 10:00 AM
    30-minute service

    Returns:

    8:00
    8:15
    8:30
    8:45
    ...
    9:30

    9:45 is excluded because the 30-minute
    service would run past 10:00.
    """

    current = datetime.combine(
        date.today(),
        start_time
    )

    closing = datetime.combine(
        date.today(),
        end_time
    )

    duration = timedelta(
        minutes=duration_minutes
    )

    slots = []

    while current + duration <= closing:
        slots.append(current.time())

        current += timedelta(
            minutes=SLOT_MINUTES
        )
    return slots

def get_available_times(
    shop_id: UUID,
    service_id: UUID,
    selected_date: date,
    barber_id: UUID | None = None
):
    """
    Return available appointment times.

    If barber_id is provided:
        Find times that barber is available.

    If barber_id is None:
        Find times where at least one barber
        is available.
    """

    day_of_week = get_day_of_week(selected_date)

    with get_connection() as conn:
        with conn.cursor() as cursor:

            # --------------------------------
            # Check shop closure
            # --------------------------------
            
            if is_shop_closed(
                cursor,
                shop_id,
                selected_date
            ):
                return []

            # --------------------------------
            # Get business hours
            # --------------------------------

            business_hours = get_business_hours(
                cursor,
                shop_id,
                day_of_week
            )

            if not business_hours:
                return []

            shop_open = business_hours[0]
            shop_close = business_hours[1]
            shop_closed = business_hours[2]

            if shop_closed:
                return []

            if shop_open is None or shop_close is None:
                return []

            # --------------------------------
            # Get service duration
            # --------------------------------

            duration_minutes = get_service_duration(
                cursor,
                shop_id,
                service_id
            )

            # --------------------------------
            # Determine barbers
            # --------------------------------

            if barber_id:
                cursor.execute(
                    """
                    SELECT id
                    FROM barbers
                    WHERE id = %s
                      AND shop_id = %s
                      AND is_active = TRUE;
                    """,
                    (
                        barber_id,
                        shop_id
                    )
                )

                barber = cursor.fetchone()
                if not barber:
                    raise ValueError(
                        "Barber not found"
                    )
                barber_ids = [barber[0]]

            else:
                cursor.execute(
                    """
                    SELECT id
                    FROM barbers
                    WHERE shop_id = %s
                      AND is_active = TRUE
                    ORDER BY name;
                    """,
                    (shop_id,)
                )

                barber_ids = [
                    row[0]
                    for row in cursor.fetchall()
                ]

            # --------------------------------
            # Generate slots for each barber
            # --------------------------------

            available_by_barber = {}
            for current_barber_id in barber_ids:
                hours = get_barber_hours(
                    cursor,
                    current_barber_id,
                    day_of_week
                )

                if not hours:
                    continue

                barber_start = hours[0]
                barber_end = hours[1]
                barber_off = hours[2]

                if barber_off:
                    continue

                if barber_start is None or barber_end is None:
                    continue

                # Barber cannot work outside
                # shop hours.

                effective_start = max(
                    barber_start,
                    shop_open
                )

                effective_end = min(
                    barber_end,
                    shop_close
                )

                if effective_start >= effective_end:
                    continue

                possible_slots = generate_slots(
                    effective_start,
                    effective_end,
                    duration_minutes
                )

                appointments = get_barber_appointments(
                    cursor,
                    current_barber_id,
                    selected_date
                )

                available_slots = []
                for slot in possible_slots:
                    appointment_start = datetime.combine(
                        selected_date,
                        slot
                    )

                    appointment_end = (
                        appointment_start
                        +
                        timedelta(
                            minutes=duration_minutes
                        )
                    )

                    conflict = False

                    for existing in appointments:

                        existing_start = existing[0]
                        existing_end = existing[1]

                        if overlaps(
                            appointment_start,
                            appointment_end,
                            existing_start,
                            existing_end
                        ):
                            conflict = True
                            break

                    if not conflict:
                        available_slots.append(
                            slot
                        )

                available_by_barber[
                    current_barber_id
                ] = available_slots

            # --------------------------------
            # Specific barber
            # --------------------------------

            if barber_id:

                return [
                    {
                        "time": slot,
                        "barber_id": barber_id
                    }
                    for slot in available_by_barber.get(
                        barber_id,
                        []
                    )
                ]

            # --------------------------------
            # Anyone available
            # --------------------------------

            combined = {}
            for current_barber_id, slots in available_by_barber.items():
                for slot in slots:
                    if slot not in combined:
                        combined[slot] = []
                    combined[slot].append(
                        current_barber_id
                    )

            return [
                {
                    "time": slot,
                    "barber_ids": barber_ids
                }
                for slot, barber_ids in sorted(
                    combined.items()
                )
            ]