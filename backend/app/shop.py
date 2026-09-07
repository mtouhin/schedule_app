from uuid import UUID

from app.db import get_connection
from app.schemas import ShopCreate

def create_shop(shop: ShopCreate):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO shops (
                    name,
                    phone,
                    email,
                    address,
                    timezone
                )
                VALUES (%s, %s, %s, %s, %s)
                RETURNING
                    id,
                    name,
                    phone,
                    email,
                    address,
                    timezone,
                    created_at;
                """,
                (
                    shop.name,
                    shop.phone,
                    shop.email,
                    shop.address,
                    shop.timezone,
                ),
            )

            return cursor.fetchone()

def get_shop(shop_id: UUID):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    name,
                    phone,
                    email,
                    address,
                    timezone,
                    created_at,
                    updated_at
                FROM shops
                WHERE id = %s;
                """,
                (shop_id,),
            )

            return cursor.fetchone()