from datetime import timedelta
from typing import Optional
from uuid import UUID

from psycopg.errors import ExclusionViolation
from psycopg.rows import dict_row

from app.db import get_connection
from app.schemas import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentStatusUpdate,
)
from app.scheduler import get_available_times


# ============================================================
# CREATE APPOINTMENT
# ============================================================

def create_appointment(
    shop_id: UUID,
    appointment: AppointmentCreate
):
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
                (
                    appointment.service_id,
                    shop_id
                )
            )

            service = cursor.fetchone()

            if not service:
                raise ValueError("Service not found")

            duration_minutes = service["duration_minutes"]

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
                raise ValueError("Customer not found")

            # --------------------------------
            # Determine barber
            # --------------------------------

            selected_barber_id = appointment.barber_id

            # --------------------------------
            # Specific barber
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
                    raise ValueError("Barber not found")

            # --------------------------------
            # Any available barber
            # --------------------------------

            else:

                available = get_available_times(
                    shop_id=shop_id,
                    service_id=appointment.service_id,
                    selected_date=appointment.start_time.date()
                )

                requested_time = appointment.start_time.time()

                matching_slot = next(
                    (
                        slot
                        for slot in available
                        if slot["time"] == requested_time
                    ),
                    None
                )

                if not matching_slot:
                    raise ValueError(
                        "The requested time is not available"
                    )

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

            requested_time = appointment.start_time.time()

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
                + timedelta(minutes=duration_minutes)
            )

            # --------------------------------
            # Insert
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
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
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
                        customer_status,
                        notes,
                        created_at,
                        updated_at;
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


# ============================================================
# GET ONE APPOINTMENT
# ============================================================

def get_appointment(
    shop_id: UUID,
    appointment_id: UUID
):
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:

            cursor.execute(
                """
                SELECT
                    id,
                    shop_id,
                    customer_id,
                    barber_id,
                    service_id,
                    start_time,
                    end_time,
                    status,
                    customer_status,
                    notes,
                    created_at,
                    updated_at
                FROM appointments
                WHERE id = %s
                  AND shop_id = %s;
                """,
                (
                    appointment_id,
                    shop_id
                )
            )

            result = cursor.fetchone()

            if not result:
                raise ValueError("Appointment not found")

            return result


# ============================================================
# GET SHOP APPOINTMENTS
# Owner/Admin only
# ============================================================

def get_shop_appointments(
    shop_id: UUID,
    selected_date=None,
    barber_id: Optional[UUID] = None,
    status: Optional[str] = None
):
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:

            query = """
                SELECT
                    a.id,
                    a.shop_id,
                    a.customer_id,
                    c.name AS customer_name,
                    c.phone AS customer_phone,
                    a.barber_id,
                    b.name AS barber_name,
                    a.service_id,
                    s.name AS service_name,
                    a.start_time,
                    a.end_time,
                    a.status,
                    a.customer_status,
                    a.notes,
                    a.created_at,
                    a.updated_at
                FROM appointments a
                JOIN customers c
                    ON a.customer_id = c.id
                LEFT JOIN barbers b
                    ON a.barber_id = b.id
                JOIN services s
                    ON a.service_id = s.id
                WHERE a.shop_id = %s
            """

            params = [shop_id]

            # --------------------------------
            # Date filter
            # --------------------------------

            if selected_date is not None:

                next_date = selected_date + timedelta(days=1)

                query += """
                    AND a.start_time >= %s
                    AND a.start_time < %s
                """

                params.extend([
                    selected_date,
                    next_date
                ])

            # --------------------------------
            # Barber filter
            # --------------------------------

            if barber_id is not None:

                query += """
                    AND a.barber_id = %s
                """

                params.append(barber_id)

            # --------------------------------
            # Status filter
            # --------------------------------

            if status is not None:

                query += """
                    AND a.status = %s
                """

                params.append(status)

            # --------------------------------
            # Sort
            # --------------------------------

            query += """
                ORDER BY a.start_time ASC;
            """

            cursor.execute(
                query,
                params
            )

            return cursor.fetchall()


# ============================================================
# GET BARBER APPOINTMENTS
# Barber only sees their own schedule
# ============================================================

def get_barber_appointments(
    barber_id: UUID,
    selected_date=None,
    status: Optional[str] = None
):
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:

            # --------------------------------
            # Verify barber
            # --------------------------------

            cursor.execute(
                """
                SELECT
                    id,
                    shop_id
                FROM barbers
                WHERE id = %s
                  AND is_active = TRUE;
                """,
                (barber_id,)
            )

            barber = cursor.fetchone()

            if not barber:
                raise ValueError("Barber not found")

            shop_id = barber["shop_id"]

            # --------------------------------
            # Build query
            # --------------------------------

            query = """
                SELECT
                    a.id,
                    a.shop_id,
                    a.customer_id,
                    c.name AS customer_name,
                    c.phone AS customer_phone,
                    a.barber_id,
                    a.service_id,
                    s.name AS service_name,
                    a.start_time,
                    a.end_time,
                    a.status,
                    a.customer_status,
                    a.notes,
                    a.created_at,
                    a.updated_at
                FROM appointments a
                JOIN customers c
                    ON a.customer_id = c.id
                JOIN services s
                    ON a.service_id = s.id
                WHERE a.barber_id = %s
                  AND a.shop_id = %s
            """

            params = [
                barber_id,
                shop_id
            ]

            # --------------------------------
            # Date filter
            # --------------------------------

            if selected_date is not None:

                next_date = selected_date + timedelta(days=1)

                query += """
                    AND a.start_time >= %s
                    AND a.start_time < %s
                """

                params.extend([
                    selected_date,
                    next_date
                ])

            # --------------------------------
            # Status filter
            # --------------------------------

            if status is not None:

                query += """
                    AND a.status = %s
                """

                params.append(status)

            # --------------------------------
            # Sort
            # --------------------------------

            query += """
                ORDER BY a.start_time ASC;
            """

            cursor.execute(
                query,
                params
            )

            return cursor.fetchall()


# ============================================================
# UPDATE APPOINTMENT
# Owner/Admin
#
# Can change:
#   - start_time
#   - barber_id
#   - notes
# ============================================================

def update_appointment(
    shop_id: UUID,
    appointment_id: UUID,
    appointment: AppointmentUpdate
):
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:

            # --------------------------------
            # Get existing appointment
            # --------------------------------

            cursor.execute(
                """
                SELECT
                    customer_id,
                    service_id,
                    barber_id,
                    start_time,
                    status,
                    notes
                FROM appointments
                WHERE id = %s
                  AND shop_id = %s;
                """,
                (
                    appointment_id,
                    shop_id
                )
            )

            existing = cursor.fetchone()

            if not existing:
                raise ValueError("Appointment not found")

            customer_id = existing["customer_id"]
            service_id = existing["service_id"]
            current_barber_id = existing["barber_id"]
            current_start_time = existing["start_time"]
            current_status = existing["status"]
            current_notes = existing["notes"]

            # --------------------------------
            # Don't modify cancelled/no-show
            # --------------------------------

            if current_status in (
                "CANCELLED",
                "NO_SHOW"
            ):
                raise ValueError(
                    "Cannot modify a cancelled or no-show appointment"
                )

            # --------------------------------
            # New values
            # --------------------------------

            new_start_time = (
                appointment.start_time
                if appointment.start_time is not None
                else current_start_time
            )

            new_barber_id = (
                appointment.barber_id
                if appointment.barber_id is not None
                else current_barber_id
            )

            new_notes = (
                appointment.notes
                if appointment.notes is not None
                else current_notes
            )

            # --------------------------------
            # Validate barber
            # --------------------------------

            if new_barber_id is not None:

                cursor.execute(
                    """
                    SELECT id
                    FROM barbers
                    WHERE id = %s
                      AND shop_id = %s
                      AND is_active = TRUE;
                    """,
                    (
                        new_barber_id,
                        shop_id
                    )
                )

                barber = cursor.fetchone()

                if not barber:
                    raise ValueError("Barber not found")

            # --------------------------------
            # Get service duration
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
                    service_id,
                    shop_id
                )
            )

            service = cursor.fetchone()

            if not service:
                raise ValueError("Service not found")

            duration_minutes = service["duration_minutes"]

            # --------------------------------
            # Check availability only when
            # barber/time is changing
            # --------------------------------

            moving_appointment = (
                new_start_time != current_start_time
                or new_barber_id != current_barber_id
            )

            if moving_appointment:

                available = get_available_times(
                    shop_id=shop_id,
                    service_id=service_id,
                    selected_date=new_start_time.date(),
                    barber_id=new_barber_id
                )

                requested_time = new_start_time.time()

                is_available = any(
                    slot["time"] == requested_time
                    for slot in available
                )

                if not is_available:
                    raise ValueError(
                        "The selected time is not available"
                    )

            # --------------------------------
            # Calculate end time
            # --------------------------------

            new_end_time = (
                new_start_time
                + timedelta(minutes=duration_minutes)
            )

            # --------------------------------
            # Update
            # --------------------------------

            try:

                cursor.execute(
                    """
                    UPDATE appointments
                    SET
                        barber_id = %s,
                        start_time = %s,
                        end_time = %s,
                        notes = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                      AND shop_id = %s
                    RETURNING
                        id,
                        shop_id,
                        customer_id,
                        barber_id,
                        service_id,
                        start_time,
                        end_time,
                        status,
                        customer_status,
                        notes,
                        created_at,
                        updated_at;
                    """,
                    (
                        new_barber_id,
                        new_start_time,
                        new_end_time,
                        new_notes,
                        appointment_id,
                        shop_id
                    )
                )

                result = cursor.fetchone()

                conn.commit()

                return result

            except ExclusionViolation:

                conn.rollback()

                raise ValueError(
                    "That time is already booked for the selected barber"
                )


# ============================================================
# UPDATE APPOINTMENT STATUS
# ============================================================

def update_appointment_status(
    shop_id: UUID,
    appointment_id: UUID,
    update: AppointmentStatusUpdate
):
    valid_statuses = {
        "BOOKED",
        "CONFIRMED",
        "RUNNING_LATE",
        "COMPLETED",
        "CANCELLED",
        "NO_SHOW",
    }

    if update.status not in valid_statuses:
        raise ValueError(
            f"Invalid appointment status: {update.status}"
        )

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:

            # --------------------------------
            # Verify appointment
            # --------------------------------

            cursor.execute(
                """
                SELECT id
                FROM appointments
                WHERE id = %s
                  AND shop_id = %s;
                """,
                (
                    appointment_id,
                    shop_id
                )
            )

            appointment = cursor.fetchone()

            if not appointment:
                raise ValueError("Appointment not found")

            # --------------------------------
            # Update
            # --------------------------------

            cursor.execute(
                """
                UPDATE appointments
                SET
                    status = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                  AND shop_id = %s
                RETURNING
                    id,
                    shop_id,
                    customer_id,
                    barber_id,
                    service_id,
                    start_time,
                    end_time,
                    status,
                    customer_status,
                    notes,
                    created_at,
                    updated_at;
                """,
                (
                    update.status,
                    appointment_id,
                    shop_id
                )
            )

            result = cursor.fetchone()

            conn.commit()

            return result