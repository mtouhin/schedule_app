from uuid import UUID
from psycopg.rows import dict_row
from app.db import get_connection
from app.schemas import ServiceCreate

def create_service(shop_id: UUID, service: ServiceCreate):
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                INSERT INTO services (
                    shop_id,
                    name,
                    description,
                    duration_minutes,
                    price_cents
                )
                VALUES (%s, %s, %s, %s, %s)
                RETURNING
                    id,
                    shop_id,
                    name,
                    description,
                    duration_minutes,
                    price_cents,
                    is_active,
                    created_at;
                """,
                (
                    shop_id,
                    service.name,
                    service.description,
                    service.duration_minutes,
                    service.price_cents,
                ),
            )

            return cursor.fetchone()

def get_services(shop_id: UUID):
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    shop_id,
                    name,
                    description,
                    duration_minutes,
                    price_cents,
                    is_active,
                    created_at
                FROM services
                WHERE shop_id = %s
                ORDER BY name;
                """,
                (shop_id,),
            )

            return cursor.fetchall()

def delete_service(shop_id: UUID, service_id: UUID):
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:

            # Make sure the service belongs to this shop
            cursor.execute(
                """
                SELECT id
                FROM services
                WHERE id = %s
                  AND shop_id = %s;
                """,
                (service_id, shop_id)
            )

            service = cursor.fetchone()

            if not service:
                raise ValueError("Service not found")

            # Check whether this service has appointments
            cursor.execute(
                """
                SELECT 1
                FROM appointments
                WHERE service_id = %s
                LIMIT 1;
                """,
                (service_id,)
            )

            appointment = cursor.fetchone()

            if appointment:
                raise ValueError(
                    "Cannot delete a service that has appointments"
                )

            # No appointments → deactivate it
            cursor.execute(
                """
                UPDATE services
                SET is_active = FALSE,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING id;
                """,
                (service_id,)
            )

            result = cursor.fetchone()

            conn.commit()

            return result["id"]
        