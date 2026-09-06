from fastapi import FastAPI, HTTPException
from uuid import UUID
from app.db_init import initialize_database
from app.schemas import ShopCreate, BarberCreate, ServiceCreate
from app.shop import create_shop, get_shop
from app.barber import create_barber, get_barbers
from app.service import create_service, get_services

app = FastAPI(
    title="Barbershop API",
    version="1.0.0"
)

#@app.on_event("startup")
#def startup():
    #initialize_database()

@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }

@app.post("/shops")
def create_shop_endpoint(shop: ShopCreate):
    shop = create_shop(shop)

    return {
        "id": shop[0],
        "name": shop[1],
        "phone": shop[2],
        "email": shop[3],
        "address": shop[4],
        "timezone": shop[5],
        "created_at": shop[6]
    }

@app.get("/shops/{shop_id}")
def get_shop_endpoint(shop_id: UUID):
    shop = get_shop(shop_id)

    if not shop:
        raise HTTPException(
            status_code=404,
            detail="Shop not found"
        )

    return {
        "id": shop[0],
        "name": shop[1],
        "phone": shop[2],
        "email": shop[3],
        "address": shop[4],
        "timezone": shop[5],
        "created_at": shop[6],
        "updated_at": shop[7]
    }

@app.post("/shops/{shop_id}/barbers")
def create_barber_endpoint(
    shop_id: UUID,
    barber: BarberCreate
):
    barber = create_barber(shop_id, barber)

    return {
        "id": barber[0],
        "shop_id": barber[1],
        "name": barber[2],
        "phone": barber[3],
        "email": barber[4],
        "is_active": barber[5],
        "created_at": barber[6]
    }

@app.get("/shops/{shop_id}/barbers")
def get_barbers_endpoint(shop_id: UUID):
    barbers = get_barbers(shop_id)

    return [
        {
            "id": barber[0],
            "shop_id": barber[1],
            "name": barber[2],
            "phone": barber[3],
            "email": barber[4],
            "is_active": barber[5],
            "created_at": barber[6]
        }
        for barber in barbers
    ]

@app.post("/shops/{shop_id}/services")
def create_service_endpoint(
    shop_id: UUID,
    service: ServiceCreate
):
    service = create_service(shop_id, service)

    return {
        "id": service[0],
        "shop_id": service[1],
        "name": service[2],
        "description": service[3],
        "duration_minutes": service[4],
        "price_cents": service[5],
        "is_active": service[6],
        "created_at": service[7]
    }


@app.get("/shops/{shop_id}/services")
def get_services_endpoint(shop_id: UUID):
    services = get_services(shop_id)

    return [
        {
            "id": service[0],
            "shop_id": service[1],
            "name": service[2],
            "description": service[3],
            "duration_minutes": service[4],
            "price_cents": service[5],
            "is_active": service[6],
            "created_at": service[7]
        }
        for service in services
    ]