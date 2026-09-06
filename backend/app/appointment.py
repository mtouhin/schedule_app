from uuid import UUID

from app.db import get_connection
from app.schemas import AppointmentCreate


def create_appointment(
    shop_id: UUID,
    appointment: AppointmentCreate
):
    with get_connection() as conn:
        with conn.cursor() as cursor:

            # Get service duration
            cursor.execute(
                """
                SELECT duration_minutes
                FROM services
                WHERE id = %s
                  AND shop_id = %s
                  AND is_active = TRUE;
                """,
                (
                    appointment.service_id,
                    shop_id
                )
            )

            service = cursor.fetchone()

            if not service:
                raise ValueError("Service not found")

            duration_minutes = service[0]

            # Calculate end time
            cursor.execute(
                """
                SELECT
                    %s + (%s * INTERVAL '1 minute');
                """,
                (
                    appointment.start_time,
                    duration_minutes
                )
            )

            end_time = cursor.fetchone()[0]

            # Make sure customer belongs to this shop
            cursor.execute(
                """
                SELECT id
                FROM customers
                WHERE id = %s
                  AND shop_id = %s;
                """,
                (
                    appointment.customer_id,
                    shop_id
                )
            )

            customer = cursor.fetchone()

            if not customer:
                raise ValueError(
                    "Customer not found"
                )

            # Make sure barber belongs to this shop
            if appointment.barber_id:

                cursor.execute(
                    """
                    SELECT id
                    FROM barbers
                    WHERE id = %s
                      AND shop_id = %s
                      AND is_active = TRUE;
                    """,
                    (
                        appointment.barber_id,
                        shop_id
                    )
                )

                barber = cursor.fetchone()

                if not barber:
                    raise ValueError(
                        "Barber not found"
                    )

            # Create appointment
            cursor.execute(
                """
                INSERT INTO appointments (
                    shop_id,
                    customer_id,
                    barber_id,
                    service_id,
                    start_time,
                    end_time,
                    status,
                    notes
                )
                VALUES (
                    %s, %s, %s, %s,
                    %s, %s,
                    'BOOKED',
                    %s
                )
                RETURNING
                    id,
                    shop_id,
                    customer_id,
                    barber_id,
                    service_id,
                    start_time,
                    end_time,
                    status,
                    notes,
                    created_at;
                """,
                (
                    shop_id,
                    appointment.customer_id,
                    appointment.barber_id,
                    appointment.service_id,
                    appointment.start_time,
                    end_time,
                    appointment.notes
                )
            )

            result = cursor.fetchone()

            conn.commit()

            return result