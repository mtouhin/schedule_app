from uuid import UUID
from psycopg.rows import dict_row
from psycopg.errors import UniqueViolation
from app.db import get_connection
from app.schemas import CustomerCreate

def create_customer(
    shop_id: UUID,
    customer: CustomerCreate
):
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:

            # Check shop exists
            cursor.execute(
                """
                SELECT id
                FROM shops
                WHERE id = %s;
                """,
                (shop_id,)
            )

            shop = cursor.fetchone()

            if not shop:
                raise ValueError("Shop not found")

            # Check for duplicate phone
            cursor.execute(
                """
                SELECT id
                FROM customers
                WHERE shop_id = %s
                  AND phone = %s;
                """,
                (
                    shop_id,
                    customer.phone
                )
            )
            
            existing_customer = cursor.fetchone()

            if existing_customer:
                raise ValueError(
                    "A customer with this phone number already exists"
                )

            # Create customer
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

            result = cursor.fetchone()
            conn.commit()

            return result

def get_customer_by_phone(shop_id: UUID, phone: str):
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
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