from uuid import UUID

from psycopg.rows import dict_row

from app.db import get_connection


def create_closure(shop_id: UUID, closure):
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:

            # Make sure the shop exists
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

            # Prevent duplicate closure for the same day
            cursor.execute(
                """
                SELECT id
                FROM shop_closures
                WHERE shop_id = %s
                  AND closure_date = %s;
                """,
                (
                    shop_id,
                    closure.closure_date
                )
            )

            existing = cursor.fetchone()

            if existing:
                raise ValueError(
                    "A closure already exists for this date"
                )

            cursor.execute(
                """
                INSERT INTO shop_closures (
                    shop_id,
                    closure_date,
                    start_time,
                    end_time,
                    reason,
                    closure_type
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING
                    id,
                    shop_id,
                    closure_date,
                    start_time,
                    end_time,
                    reason,
                    closure_type,
                    created_at;
                """,
                (
                    shop_id,
                    closure.closure_date,
                    closure.start_time,
                    closure.end_time,
                    closure.reason,
                    closure.closure_type
                )
            )

            result = cursor.fetchone()

            conn.commit()

            return result


def get_closures(shop_id: UUID):
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:

            cursor.execute(
                """
                SELECT
                    id,
                    shop_id,
                    closure_date,
                    start_time,
                    end_time,
                    reason,
                    closure_type,
                    created_at
                FROM shop_closures
                WHERE shop_id = %s
                ORDER BY closure_date;
                """,
                (shop_id,)
            )

            return cursor.fetchall()


def get_closure(shop_id: UUID, closure_id: UUID):
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:

            cursor.execute(
                """
                SELECT
                    id,
                    shop_id,
                    closure_date,
                    start_time,
                    end_time,
                    reason,
                    closure_type,
                    created_at
                FROM shop_closures
                WHERE id = %s
                  AND shop_id = %s;
                """,
                (
                    closure_id,
                    shop_id
                )
            )

            return cursor.fetchone()


def delete_closure(shop_id: UUID, closure_id: UUID):
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:

            cursor.execute(
                """
                DELETE FROM shop_closures
                WHERE id = %s
                  AND shop_id = %s
                RETURNING id;
                """,
                (
                    closure_id,
                    shop_id
                )
            )

            result = cursor.fetchone()

            if not result:
                raise ValueError("Closure not found")

            conn.commit()

            return result["id"]