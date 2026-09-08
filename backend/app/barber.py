from uuid import UUID
from psycopg.errors import UniqueViolation
from app.db import get_connection
from app.schemas import BarberCreate

def create_barber(shop_id: UUID, barber: BarberCreate):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute(
                    """
                    INSERT INTO barbers (
                        shop_id, name, phone, email
                    )
                    VALUES (%s, %s, %s, %s)
                    RETURNING
                        id, shop_id, name, phone, email,
                        is_active, created_at;
                    """,
                    (
                        shop_id,
                        barber.name,
                        barber.phone,
                        barber.email
                    ),
                )

                result = cursor.fetchone()
                conn.commit()
                return result

            except UniqueViolation as e:
                conn.rollback()

                raise ValueError(
                    "A barber with that name, phone, or email already exists"
                )

def get_barbers(shop_id: UUID):
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
                    is_active,
                    created_at
                FROM barbers
                WHERE shop_id = %s
                ORDER BY name;
                """,
                (shop_id,),
            )

            return cursor.fetchall()