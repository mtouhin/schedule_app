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
                         AppointmentCreate,
                         AppointmentUpdate,
                         AppointmentStatusUpdate)

from app.shop import create_shop, get_shop, delete_shop
from app.barber import create_barber, get_barbers
from app.service import create_service, get_services, delete_service
from app.business_hours import set_business_hours, get_business_hours
from app.barber_hours import set_barber_hours, get_barber_hours
from app.customer import get_customer_by_phone, create_customer
from app.appointment import (create_appointment,
                             get_appointment,
                             get_shop_appointments,
                             get_barber_appointments,
                             update_appointment,
                             update_appointment_status)

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
        "id": shop["id"],
        "name": shop["name"],
        "phone": shop["phone"],
        "email": shop["email"],
        "address": shop["address"],
        "timezone": shop["timezone"],
        "created_at": shop["created_at"]
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
        "id": shop["id"],
        "name": shop["name"],
        "phone": shop["phone"],
        "email": shop["email"],
        "address": shop["address"],
        "timezone": shop["timezone"],
        "created_at": shop["created_at"],
        "updated_at": shop["updated_at"]
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
        "id": result["id"],
        "shop_id": result["shop_id"],
        "day_of_week": result["day_of_week"],
        "open_time": result["open_time"],
        "close_time": result["close_time"],
        "is_closed": result["is_closed"]
    }


@app.get("/shops/{shop_id}/business-hours")
def get_business_hours_endpoint(shop_id: UUID):

    hours = get_business_hours(shop_id)

    return [
        {
            "id": row["id"],
            "shop_id": row["shop_id"],
            "day_of_week": row["day_of_week"],
            "open_time": row["open_time"],
            "close_time": row["close_time"],
            "is_closed": row["is_closed"]
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
            "id": barber["id"],
            "shop_id": barber["shop_id"],
            "name": barber["name"],
            "phone": barber["phone"],
            "email": barber["email"],
            "is_active": barber["is_active"],
            "created_at": barber["created_at"]
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
            "id": barber["id"],
            "shop_id": barber["shop_id"],
            "name": barber["name"],
            "phone": barber["phone"],
            "email": barber["email"],
            "is_active": barber["is_active"],
            "created_at": barber["created_at"]
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
            "id": row["id"],
            "barber_id": row["barber_id"],
            "day_of_week": row["day_of_week"],
            "start_time": row["start_time"],
            "end_time": row["end_time"],
            "is_off": row["is_off"]
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
            "id": result["id"],
            "barber_id": result["barber_id"],
            "day_of_week": result["day_of_week"],
            "start_time": result["start_time"],
            "end_time": result["end_time"],
            "is_off": result["is_off"]
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
        "id": service["id"],
        "shop_id": service["shop_id"],
        "name": service["name"],
        "description": service["description"],
        "duration_minutes": service["duration_minutes"],
        "price_cents": service["price_cents"],
        "is_active": service["is_active"],
        "created_at": service["created_at"]
    }


@app.get("/shops/{shop_id}/services")
def get_services_endpoint(shop_id: UUID):
    services = get_services(shop_id)

    return [
        {
            "id": service["id"],
            "shop_id": service["shop_id"],
            "name": service["name"],
            "description": service["description"],
            "duration_minutes": service["duration_minutes"],
            "price_cents": service["price_cents"],
            "is_active": service["is_active"],
            "created_at": service["created_at"]
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
            "id": result["id"],
            "shop_id": result["shop_id"],
            "name": result["name"],
            "phone": result["phone"],
            "email": result["email"],
            "created_at": result["created_at"]
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
        "id": customer["id"],
        "shop_id": customer["shop_id"],
        "name": customer["name"],
        "phone": customer["phone"],
        "email": customer["email"],
        "created_at": customer["created_at"],
        "updated_at": customer["updated_at"]
    }

@app.post("/shops/{shop_id}/appointments")
def create_appointment_endpoint(
    shop_id: UUID,
    appointment: AppointmentCreate
):
    try:
        result = create_appointment(
            shop_id=shop_id,
            appointment=appointment
        )

        return {
            "id": result["id"],
            "shop_id": result["shop_id"],
            "customer_id": result["customer_id"],
            "barber_id": result["barber_id"],
            "service_id": result["service_id"],
            "start_time": result["start_time"],
            "end_time": result["end_time"],
            "status": result["status"],
            "notes": result["notes"]
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

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

@app.get("/shops/{shop_id}/appointments/{appointment_id}")
def get_appointment_endpoint(
    shop_id: UUID,
    appointment_id: UUID
):
    try:
        return get_appointment(
            shop_id,
            appointment_id
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

@app.get("/shops/{shop_id}/appointments")
def get_shop_appointments_endpoint(
    shop_id: UUID,
    date: Optional[date] = None,
    barber_id: Optional[UUID] = None,
    status: Optional[str] = None
):
    try:
        
        appointments = get_shop_appointments(
            shop_id=shop_id,
            selected_date=date,
            barber_id=barber_id,
            status=status
        )

        return {
            "appointments": appointments
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/barbers/{barber_id}/appointments")
def get_barber_appointments_endpoint(
    barber_id: UUID,
    date: Optional[date] = None,
    status: Optional[str] = None
):
    try:

        appointments = get_barber_appointments(
            barber_id=barber_id,
            selected_date=date,
            status=status
        )

        return {
            "appointments": appointments
        }

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

@app.patch("/shops/{shop_id}/appointments/{appointment_id}")
def update_appointment_endpoint(
    shop_id: UUID,
    appointment_id: UUID,
    appointment: AppointmentUpdate
):
    try:

        return update_appointment(
            shop_id=shop_id,
            appointment_id=appointment_id,
            appointment=appointment
        )

    except ValueError as e:

        message = str(e)

        if message == "Appointment not found":
            raise HTTPException(
                status_code=404,
                detail=message
            )

        raise HTTPException(
            status_code=409,
            detail=message
        )

@app.patch("/shops/{shop_id}/appointments/{appointment_id}/status")
def update_appointment_status_endpoint(
    shop_id: UUID,
    appointment_id: UUID,
    update: AppointmentStatusUpdate
):
    try:

        return update_appointment_status(
            shop_id=shop_id,
            appointment_id=appointment_id,
            update=update
        )

    except ValueError as e:

        message = str(e)

        if message == "Appointment not found":
            raise HTTPException(
                status_code=404,
                detail=message
            )

        raise HTTPException(
            status_code=400,
            detail=message
        )