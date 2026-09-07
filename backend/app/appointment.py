from datetime import timedelta
from uuid import UUID
from psycopg.errors import ExclusionViolation
from app.db import get_connection
from app.schemas import AppointmentCreate
from app.scheduler import get_available_times


def create_appointment(
    shop_id: UUID,
    appointment: AppointmentCreate
):
    with get_connection() as conn:
        with conn.cursor() as cursor:

            # --------------------------------
            # Get service
            # --------------------------------

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
                raise ValueError(
                    "Service not found"
                )

            duration_minutes = service[0]


            # --------------------------------
            # Validate customer
            # --------------------------------

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


            # --------------------------------
            # Determine barber
            # --------------------------------

            selected_barber_id = appointment.barber_id


            # --------------------------------
            # If specific barber was selected
            # --------------------------------

            if selected_barber_id:

                cursor.execute(
                    """
                    SELECT id
                    FROM barbers
                    WHERE id = %s
                      AND shop_id = %s
                      AND is_active = TRUE;
                    """,
                    (
                        selected_barber_id,
                        shop_id
                    )
                )

                barber = cursor.fetchone()

                if not barber:
                    raise ValueError(
                        "Barber not found"
                    )


            # --------------------------------
            # If "any barber" was selected
            # --------------------------------

            else:

                available = get_available_times(
                    shop_id=shop_id,
                    service_id=appointment.service_id,
                    selected_date=appointment.start_time.date()
                )

                requested_time = (
                    appointment.start_time.time()
                )

                matching_slot = None

                for slot in available:

                    if slot["time"] == requested_time:
                        matching_slot = slot
                        break

                if not matching_slot:
                    raise ValueError(
                        "The requested time is not available"
                    )

                # Pick the first available barber.
                selected_barber_id = (
                    matching_slot["barber_ids"][0]
                )


            # --------------------------------
            # Final availability check
            # --------------------------------

            available = get_available_times(
                shop_id=shop_id,
                service_id=appointment.service_id,
                selected_date=appointment.start_time.date(),
                barber_id=selected_barber_id
            )

            requested_time = (
                appointment.start_time.time()
            )

            is_available = any(
                slot["time"] == requested_time
                for slot in available
            )

            if not is_available:
                raise ValueError(
                    "The selected time is no longer available"
                )


            # --------------------------------
            # Calculate end time
            # --------------------------------

            end_time = (
                appointment.start_time
                +
                timedelta(
                    minutes=duration_minutes
                )
            )


            # --------------------------------
            # Create appointment
            # --------------------------------

            try:
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
                    VALUES (%s, %s, %s, %s, %s, %s, 'BOOKED', %s)
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
                        selected_barber_id,
                        appointment.service_id,
                        appointment.start_time,
                        end_time,
                        appointment.notes
                    )
                )
                result = cursor.fetchone()
                conn.commit()
                return result

            except ExclusionViolation:
                conn.rollback()

                raise ValueError(
                    "That time was just booked by another customer. "
                    "Please choose another time."
                )