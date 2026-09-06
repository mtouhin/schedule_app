from uuid import UUID

from app.db import get_connection
from app.schemas import BusinessHoursCreate


def set_business_hours(
    shop_id: UUID,
    hours: BusinessHoursCreate
):
    with get_connection() as conn:
        with conn.cursor() as cursor:

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
                (shop_id, hours.day_of_week)
            )

            existing = cursor.fetchone()

            if existing:
                cursor.execute(
                    """
                    UPDATE business_hours
                    SET
                        open_time = %s,
                        close_time = %s,
                        is_closed = %s
                    WHERE shop_id = %s
                      AND day_of_week = %s
                    RETURNING
                        id,
                        shop_id,
                        day_of_week,
                        open_time,
                        close_time,
                        is_closed;
                    """,
                    (
                        hours.open_time,
                        hours.close_time,
                        hours.is_closed,
                        shop_id,
                        hours.day_of_week
                    )
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO business_hours (
                        shop_id,
                        day_of_week,
                        open_time,
                        close_time,
                        is_closed
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING
                        id,
                        shop_id,
                        day_of_week,
                        open_time,
                        close_time,
                        is_closed;
                    """,
                    (
                        shop_id,
                        hours.day_of_week,
                        hours.open_time,
                        hours.close_time,
                        hours.is_closed
                    )
                )

            return cursor.fetchone()


def get_business_hours(shop_id: UUID):

    with get_connection() as conn:
        with conn.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    id,
                    shop_id,
                    day_of_week,
                    open_time,
                    close_time,
                    is_closed
                FROM business_hours
                WHERE shop_id = %s
                ORDER BY day_of_week;
                """,
                (shop_id,)
            )

            return cursor.fetchall()