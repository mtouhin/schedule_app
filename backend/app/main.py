from fastapi import FastAPI, HTTPException
from uuid import UUID
from app.db_init import initialize_database
from app.schemas import ShopCreate, BarberCreate, ServiceCreate, BusinessHoursCreate, BarberHoursCreate
from app.shop import create_shop, get_shop
from app.barber import create_barber, get_barbers
from app.service import create_service, get_services
from app.business_hours import set_business_hours, get_business_hours
from app.barber_hours import set_barber_hours, get_barber_hours

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
    
@app.put("/shops/{shop_id}/business-hours")
def set_business_hours_endpoint(
    shop_id: UUID,
    hours: BusinessHoursCreate
):
    if not hours.is_closed:

        if hours.open_time is None or hours.close_time is None:
            raise HTTPException(
                status_code=400,
                detail="Open and close times are required when business is open"
            )

        if hours.close_time <= hours.open_time:
            raise HTTPException(
                status_code=400,
                detail="Closing time must be after opening time"
            )

    result = set_business_hours(shop_id, hours)

    return {
        "id": result[0],
        "shop_id": result[1],
        "day_of_week": result[2],
        "open_time": result[3],
        "close_time": result[4],
        "is_closed": result[5]
    }


@app.get("/shops/{shop_id}/business-hours")
def get_business_hours_endpoint(shop_id: UUID):

    hours = get_business_hours(shop_id)

    return [
        {
            "id": row[0],
            "shop_id": row[1],
            "day_of_week": row[2],
            "open_time": row[3],
            "close_time": row[4],
            "is_closed": row[5]
        }
        for row in hours
    ]

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
@app.get("/barbers/{barber_id}/hours")
def get_barber_hours_endpoint(
    barber_id: UUID
):

    hours = get_barber_hours(barber_id)

    return [
        {
            "id": row[0],
            "barber_id": row[1],
            "day_of_week": row[2],
            "start_time": row[3],
            "end_time": row[4],
            "is_off": row[5]
        }
        for row in hours
    ]

@app.put("/barbers/{barber_id}/hours")
def set_barber_hours_endpoint(
    barber_id: UUID,
    hours: BarberHoursCreate
):
    try:
        result = set_barber_hours(
            barber_id,
            hours
        )

        return {
            "id": result[0],
            "barber_id": result[1],
            "day_of_week": result[2],
            "start_time": result[3],
            "end_time": result[4],
            "is_off": result[5]
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

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