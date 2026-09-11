from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime, time
from uuid import UUID
from typing import Optional

class ShopCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    timezone: str = "America/Chicago"

def parse_time(value):
    if value is None:
        return None

    if isinstance(value, time):
        return value

    value = value.strip().upper()

    for fmt in ("%I:%M %p", "%I %p"):
        try:
            return datetime.strptime(value, fmt).time()
        except ValueError:
            continue

    raise ValueError(
        "Time must be in format like '9:00 AM'"
    )

class BarberCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Barber name cannot be empty")

        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):
        if value is None:
            return value

        value = value.strip()

        if not value:
            return None

        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        if value is None:
            return value

        value = value.strip().lower()

        if not value:
            return None

        return value

class ServiceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    duration_minutes: int
    price_cents: int

class BusinessHoursCreate(BaseModel):
    day_of_week: int
    open_time: Optional[time] = None
    close_time: Optional[time] = None
    is_closed: bool = False

    @field_validator("open_time", "close_time", mode="before")
    @classmethod
    def parse_times(cls, value):
        return parse_time(value)

    @field_validator("open_time", "close_time")
    @classmethod
    def validate_time(cls, value):
        if value is None:
            return value

        if value.minute % 15 != 0:
            raise ValueError(
                "Time must be in 15-minute increments"
            )

        if value < time(5, 0):
            raise ValueError(
                "Time cannot be earlier than 5:00 AM"
            )

        if value > time(23, 45):
            raise ValueError(
                "Time cannot be later than 11:45 PM"
            )

        return value

class BarberHoursCreate(BaseModel):
    day_of_week: int
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_off: bool = False

    @field_validator("start_time", "end_time", mode="before")
    @classmethod
    def parse_times(cls, value):
        return parse_time(value)

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_time(cls, value):
        if value is None:
            return value

        if value.minute % 15 != 0:
            raise ValueError(
                "Time must be in 15-minute increments"
            )

        if value < time(5, 0):
            raise ValueError(
                "Time cannot be earlier than 5:00 AM"
            )

        if value > time(23, 45):
            raise ValueError(
                "Time cannot be later than 11:45 PM"
            )

        return value
    
class CustomerCreate(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Name cannot be empty")

        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Phone cannot be empty")

        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        if value is None:
            return None

        value = value.strip().lower()

        if not value:
            return None

        return value
    
class AppointmentCreate(BaseModel):
    customer_id: UUID
    service_id: UUID
    barber_id: Optional[UUID] = None
    start_time: datetime
    notes: Optional[str] = None
    
    @field_validator("start_time")
    @classmethod
    def validate_start_time(cls, value):
        if value.tzinfo is not None:
            raise ValueError(
                "start_time must not include a timezone"
            )

        return value

class AppointmentUpdate(BaseModel):
    start_time: Optional[datetime] = None
    barber_id: Optional[UUID] = None
    notes: Optional[str] = None

    @field_validator("start_time")
    @classmethod
    def validate_start_time(cls, value):
        if value is not None and value.tzinfo is not None:
            raise ValueError(
                "start_time must not include a timezone"
            )

        return value

class AppointmentStatusUpdate(BaseModel):
    status: str