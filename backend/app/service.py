from uuid import UUID

from app.db import get_connection
from app.schemas import ServiceCreate

def create_service(shop_id: UUID, service: ServiceCreate):
    with get_connection() as conn:
        with conn.cursor() as cursor:
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
        with conn.cursor() as cursor:
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