from uuid import UUID

from app.db import get_connection
from app.schemas import CustomerCreate


def create_customer(shop_id: UUID, customer: CustomerCreate):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO customers (
                    shop_id,
                    name,
                    phone,
                    email
                )
                VALUES (%s, %s, %s, %s)
                RETURNING
                    id,
                    shop_id,
                    name,
                    phone,
                    email,
                    created_at;
                """,
                (
                    shop_id,
                    customer.name,
                    customer.phone,
                    customer.email
                )
            )

            return cursor.fetchone()

def get_customer_by_phone(shop_id: UUID, phone: str):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    shop_id,
                    name,
                    phone,
                    email,
                    created_at,
                    updated_at
                FROM customers
                WHERE shop_id = %s
                  AND phone = %s;
                """,
                (shop_id, phone)
            )

            return cursor.fetchone()