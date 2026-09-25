from typing import Optional
from uuid import UUID
from datetime import datetime
from psycopg.rows import dict_row
from .db import get_connection

def create_notification(
    appointment_id: UUID,
    notification_type: str,
    channel: str,
    recipient_type: str,
    recipient: str,
    message: str,
    recipient_id: Optional[UUID] = None,
    scheduled_for: Optional[datetime] = None,
):
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                INSERT INTO notifications (
                    appointment_id,
                    type,
                    channel,
                    recipient_type,
                    recipient_id,
                    recipient,
                    message,
                    status,
                    scheduled_for
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, 'pending', %s
                )
                RETURNING
                    id,
                    appointment_id,
                    type,
                    channel,
                    recipient_type,
                    recipient_id,
                    recipient,
                    message,
                    status,
                    scheduled_for,
                    sent_at,
                    failed_at,
                    error_message,
                    created_at;
                """,
                (
                    appointment_id,
                    notification_type,
                    channel,
                    recipient_type,
                    recipient_id,
                    recipient,
                    message,
                    scheduled_for,
                ),
            )

            result = cursor.fetchone()

            conn.commit()

            return result

def build_customer_confirmation_message(
    customer_name: str,
    service_name: str,
    barber_name: str,
    start_time: str,
) -> str:
    return (
        f"Hi {customer_name}, your appointment is confirmed. "
        f"{service_name} with {barber_name} "
        f"at {start_time}."
    )

def build_barber_confirmation_message(
    customer_name: str,
    service_name: str,
    start_time: str,
) -> str:
    return (
        f"New appointment: {customer_name} booked "
        f"{service_name} at {start_time}."
    )

def build_customer_rescheduled_message(
    customer_name: str,
    service_name: str,
    barber_name: str,
    start_time: str,
) -> str:
    return (
        f"Hi {customer_name}, your appointment has been "
        f"rescheduled to {start_time} with {barber_name}."
    )

def build_barber_rescheduled_message(
    customer_name: str,
    service_name: str,
    start_time: str,
) -> str:
    return (
        f"Appointment update: {customer_name}'s "
        f"{service_name} appointment was rescheduled to "
        f"{start_time}."
    )

def build_customer_cancelled_message(
    customer_name: str,
    service_name: str,
    start_time: str,
) -> str:
    return (
        f"Hi {customer_name}, your {service_name} appointment "
        f"at {start_time} has been cancelled."
    )

def build_barber_cancelled_message(
    customer_name: str,
    service_name: str,
    start_time: str,
) -> str:
    return (
        f"Appointment cancelled: {customer_name}'s "
        f"{service_name} appointment at {start_time} "
        f"was cancelled."
    )

def notify_appointment_created(
    appointment,
    customer,
    barber,
    service,
):
    customer_message = build_customer_confirmation_message(
        customer_name=customer["name"],
        service_name=service["name"],
        barber_name=barber["name"],
        start_time=str(appointment["start_time"]),
    )

    barber_message = build_barber_confirmation_message(
        customer_name=customer["name"],
        service_name=service["name"],
        start_time=str(appointment["start_time"]),
    )

    create_notification(
        appointment_id=appointment["id"],
        notification_type="confirmation",
        channel="sms",
        recipient_type="customer",
        recipient_id=customer["id"],
        recipient=customer["phone"],
        message=customer_message,
    )

    create_notification(
        appointment_id=appointment["id"],
        notification_type="confirmation",
        channel="sms",
        recipient_type="barber",
        recipient_id=barber["id"],
        recipient=barber["phone"],
        message=barber_message,
    )

def notify_appointment_rescheduled(
    appointment,
    customer,
    barber,
    service,
):
    customer_message = build_customer_rescheduled_message(
        customer_name=customer["name"],
        service_name=service["name"],
        barber_name=barber["name"],
        start_time=str(appointment["start_time"]),
    )

    barber_message = build_barber_rescheduled_message(
        customer_name=customer["name"],
        service_name=service["name"],
        start_time=str(appointment["start_time"]),
    )

    create_notification(
        appointment_id=appointment["id"],
        notification_type="rescheduled",
        channel="sms",
        recipient_type="customer",
        recipient_id=customer["id"],
        recipient=customer["phone"],
        message=customer_message,
    )

    create_notification(
        appointment_id=appointment["id"],
        notification_type="rescheduled",
        channel="sms",
        recipient_type="barber",
        recipient_id=barber["id"],
        recipient=barber["phone"],
        message=barber_message,
    )

def notify_appointment_cancelled(
    appointment,
    customer,
    barber,
    service,
):
    customer_message = build_customer_cancelled_message(
        customer_name=customer["name"],
        service_name=service["name"],
        start_time=str(appointment["start_time"]),
    )

    barber_message = build_barber_cancelled_message(
        customer_name=customer["name"],
        service_name=service["name"],
        start_time=str(appointment["start_time"]),
    )

    create_notification(
        appointment_id=appointment["id"],
        notification_type="cancelled",
        channel="sms",
        recipient_type="customer",
        recipient_id=customer["id"],
        recipient=customer["phone"],
        message=customer_message,
    )

    create_notification(
        appointment_id=appointment["id"],
        notification_type="cancelled",
        channel="sms",
        recipient_type="barber",
        recipient_id=barber["id"],
        recipient=barber["phone"],
        message=barber_message,
    )