from uuid import UUID

from app.db import get_connection
from app.schemas import ShopCreate
from psycopg.rows import dict_row

def create_shop(shop: ShopCreate):
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
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
        with conn.cursor(row_factory=dict_row) as cursor:
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

def delete_shop(shop_id: UUID):
    with get_connection() as conn:
        with conn.cursor() as cursor:

            cursor.execute(
                """
                DELETE FROM shops
                WHERE id = %s
                RETURNING id;
                """,
                (shop_id,)
            )

            result = cursor.fetchone()

            if not result:
                raise ValueError("Shop not found")

            conn.commit()

            return result[0]