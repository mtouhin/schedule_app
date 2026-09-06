from uuid import UUID

from app.db import get_connection
from app.schemas import BarberHoursCreate
from datetime import time

def make_time_naive(value):
    if value is None:
        return None

    return time(
        value.hour,
        value.minute,
        value.second,
        value.microsecond
    )

def set_barber_hours(
    barber_id: UUID,
    hours: BarberHoursCreate
):
    with get_connection() as conn:
        with conn.cursor() as cursor:

            # ------------------------------------------------
            # 1. Make sure barber exists and get their shop
            # ------------------------------------------------

            cursor.execute(
                """
                SELECT shop_id
                FROM barbers
                WHERE id = %s
                  AND is_active = TRUE;
                """,
                (barber_id,)
            )

            barber = cursor.fetchone()

            if not barber:
                raise ValueError("Barber not found")

            shop_id = barber[0]

            # ------------------------------------------------
            # 2. If barber is OFF, no times are needed
            # ------------------------------------------------

            if hours.is_off:

                cursor.execute(
                    """
                    INSERT INTO barber_hours (
                        barber_id,
                        day_of_week,
                        start_time,
                        end_time,
                        is_off
                    )
                    VALUES (%s, %s, NULL, NULL, TRUE)

                    ON CONFLICT (barber_id, day_of_week)
                    DO UPDATE SET
                        start_time = NULL,
                        end_time = NULL,
                        is_off = TRUE

                    RETURNING
                        id,
                        barber_id,
                        day_of_week,
                        start_time,
                        end_time,
                        is_off;
                    """,
                    (
                        barber_id,
                        hours.day_of_week
                    )
                )

                result = cursor.fetchone()
                conn.commit()

                return result

            # ------------------------------------------------
            # 3. If working, times are required
            # ------------------------------------------------

            if hours.start_time is None or hours.end_time is None:
                raise ValueError(
                    "Start and end times are required when barber is working"
                )

            # ------------------------------------------------
            # 4. End time must be after start time
            # ------------------------------------------------

            if hours.end_time <= hours.start_time:
                raise ValueError(
                    "End time must be after start time"
                )

            # ------------------------------------------------
            # 5. Get shop's business hours for this day
            # ------------------------------------------------

            cursor.execute(
                """
                SELECT
                    open_time::time,
                    close_time::time,
                    is_closed
                FROM business_hours
                WHERE shop_id = %s
                  AND day_of_week = %s;
                """,
                (
                    shop_id,
                    hours.day_of_week
                )
            )

            shop_hours = cursor.fetchone()

            if not shop_hours:
                raise ValueError(
                    "Business hours have not been configured for this day"
                )

            shop_open = make_time_naive(shop_hours[0])
            shop_close = make_time_naive(shop_hours[1])
            shop_closed = shop_hours[2]
            
            start_time = make_time_naive(hours.start_time)
            end_time = make_time_naive(hours.end_time)
            print("hours.start_time:", hours.start_time, hours.start_time.tzinfo)
            print("shop_open:", shop_open, shop_open.tzinfo)

            # ------------------------------------------------
            # 6. Shop must actually be open
            # ------------------------------------------------

            if shop_closed:
                raise ValueError(
                    "Barber cannot work because the shop is closed on this day"
                )

            # ------------------------------------------------
            # 7. Shop must have valid hours
            # ------------------------------------------------

            if shop_open is None or shop_close is None:
                raise ValueError(
                    "Shop business hours are incomplete"
                )

            # ------------------------------------------------
            # 8. Barber cannot start before shop opens
            # ------------------------------------------------
            if start_time < shop_open:
                raise ValueError(
                    "Barber cannot start before the shop opens"
                )

            # ------------------------------------------------
            # 9. Barber cannot finish after shop closes
            # ------------------------------------------------

            if end_time > shop_close:
                raise ValueError(
                    "Barber cannot work after the shop closes"
                )

            # ------------------------------------------------
            # 10. Save/update barber hours
            # ------------------------------------------------

            cursor.execute(
                """
                INSERT INTO barber_hours (
                    barber_id,
                    day_of_week,
                    start_time,
                    end_time,
                    is_off
                )
                VALUES (%s, %s, %s, %s, FALSE)

                ON CONFLICT (barber_id, day_of_week)
                DO UPDATE SET
                    start_time = EXCLUDED.start_time,
                    end_time = EXCLUDED.end_time,
                    is_off = FALSE

                RETURNING
                    id,
                    barber_id,
                    day_of_week,
                    start_time,
                    end_time,
                    is_off;
                """,
                (
                    barber_id,
                    hours.day_of_week,
                    start_time,
                    end_time
                )
            )

            result = cursor.fetchone()

            conn.commit()

            return result


def get_barber_hours(barber_id: UUID):

    with get_connection() as conn:
        with conn.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    id,
                    barber_id,
                    day_of_week,
                    start_time,
                    end_time,
                    is_off
                FROM barber_hours
                WHERE barber_id = %s
                ORDER BY day_of_week;
                """,
                (barber_id,)
            )

            return cursor.fetchall()