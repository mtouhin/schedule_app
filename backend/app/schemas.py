from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import time

class ShopCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    timezone: str = "America/Chicago"

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

    @field_validator("day_of_week")
    @classmethod
    def validate_day(cls, value):
        if value < 0 or value > 6:
            raise ValueError("day_of_week must be between 0 and 6")

        return value

    @field_validator("open_time", "close_time")
    @classmethod
    def validate_time(cls, value):
        if value is None:
            return value

        # 15-minute increments
        if value.minute % 15 != 0 or value.second != 0:
            raise ValueError("Time must be in 15-minute increments")

        # Reasonable business hours
        if value.hour < 5:
            raise ValueError("Business cannot open before 5:00 AM")

        if value.hour > 23:
            raise ValueError("Business cannot operate after 11:45 PM")

        return value

class BarberHoursCreate(BaseModel):
    day_of_week: int
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_off: bool = False

    @field_validator("day_of_week")
    @classmethod
    def validate_day(cls, value):
        if value < 0 or value > 6:
            raise ValueError("day_of_week must be between 0 and 6")

        return value

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_time(cls, value):
        if value is None:
            return value

        if value.minute % 15 != 0 or value.second != 0:
            raise ValueError("Time must be in 15-minute increments")

        if value.hour < 5:
            raise ValueError("Barber cannot start before 5:00 AM")

        if value.hour > 23:
            raise ValueError("Barber cannot work after 11:45 PM")

        return value