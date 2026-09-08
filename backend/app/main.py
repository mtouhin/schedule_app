from fastapi import FastAPI, HTTPException
from uuid import UUID
from datetime import date
from typing import Optional
from app.db_init import initialize_database
from app.schemas import (ShopCreate, 
                         BarberCreate, 
                         ServiceCreate, 
                         BusinessHoursCreate, 
                         BarberHoursCreate, 
                         CustomerCreate,
                         AppointmentCreate)

from app.shop import create_shop, get_shop, delete_shop
from app.barber import create_barber, get_barbers
from app.service import create_service, get_services, delete_service
from app.business_hours import set_business_hours, get_business_hours
from app.barber_hours import set_barber_hours, get_barber_hours
from app.customer import get_customer_by_phone, create_customer
from app.appointment import create_appointment
from app.scheduler import get_available_times

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

@app.delete("/shops/{shop_id}")
def delete_shop_endpoint(shop_id: UUID):

    try:
        deleted_id = delete_shop(shop_id)

        return {
            "message": "Shop deleted",
            "id": deleted_id
        }

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

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
    try:
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
    except ValueError as e:
        raise HTTPException(
            status_code=409,
            detail=str(e)
        )

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

@app.delete("/shops/{shop_id}/services/{service_id}")
def delete_service_endpoint(
    shop_id: UUID,
    service_id: UUID
):
    try:
        deleted_id = delete_service(
            shop_id,
            service_id
        )

        return {
            "message": "Service deactivated",
            "id": deleted_id
        }

    except ValueError as e:
        if str(e) == "Service not found":
            raise HTTPException(
                status_code=404,
                detail=str(e)
            )

        raise HTTPException(
            status_code=409,
            detail=str(e)
        )

@app.post("/shops/{shop_id}/customers")
def create_customer_endpoint(
    shop_id: UUID,
    customer: CustomerCreate
):
    try:
        result = create_customer(shop_id, customer)

        return {
            "id": result[0],
            "shop_id": result[1],
            "name": result[2],
            "phone": result[3],
            "email": result[4],
            "created_at": result[5]
        }

    except ValueError as e:
        raise HTTPException(
            status_code=409,
            detail=str(e)
        )

@app.get("/shops/{shop_id}/customers/phone/{phone}")
def get_customer_by_phone_endpoint(
    shop_id: UUID,
    phone: str
):
    customer = get_customer_by_phone(shop_id, phone)

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    return {
        "id": customer[0],
        "shop_id": customer[1],
        "name": customer[2],
        "phone": customer[3],
        "email": customer[4],
        "created_at": customer[5],
        "updated_at": customer[6]
    }

@app.post("/shops/{shop_id}/appointments")
def create_appointment_endpoint(
    shop_id: UUID,
    appointment: AppointmentCreate
):
    try:

        result = create_appointment(
            shop_id,
            appointment
        )

        return {
            "id": result[0],
            "shop_id": result[1],
            "customer_id": result[2],
            "barber_id": result[3],
            "service_id": result[4],
            "start_time": result[5],
            "end_time": result[6],
            "status": result[7],
            "notes": result[8],
            "created_at": result[9]
        }

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@app.get("/shops/{shop_id}/availability")
def get_availability_endpoint(
    shop_id: UUID,
    service_id: UUID,
    date: date,
    barber_id: Optional[UUID] = None
):
    try:
        available = get_available_times(
            shop_id=shop_id,
            service_id=service_id,
            selected_date=date,
            barber_id=barber_id
        )

        return {
            "date": date,
            "service_id": service_id,
            "barber_id": barber_id,
            "available_times": available
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )