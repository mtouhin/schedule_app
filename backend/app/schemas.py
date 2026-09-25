from pydantic import BaseModel, field_validator, model_validator
from typing import Optional
from datetime import datetime, date, time
from uuid import UUID
from enum import Enum
from typing import Optional

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

class ShopCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    timezone: str = "America/Chicago"
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        value = value.strip()
        
        if not value:
            raise ValueError("Shop name cannot be empty")
        return value
    
    @field_validator("address")
    @classmethod
    def validate_address(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Address cannot be empty")

        return value

class ShopClosureCreate(BaseModel):
    closure_date: date
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    reason: Optional[str] = None
    closure_type: str = "HOLIDAY"

    @model_validator(mode="after")
    def validate_times(self):
        if (self.start_time is None) != (self.end_time is None):
            raise ValueError(
                "Both start_time and end_time are required for a partial-day closure"
            )

        if (
            self.start_time is not None
            and self.end_time is not None
            and self.end_time <= self.start_time
        ):
            raise ValueError(
                "Closure end time must be after start time"
            )

        return self

    @field_validator("closure_type")
    @classmethod
    def validate_closure_type(cls, value):
        value = value.strip().upper()

        allowed = {"HOLIDAY", "EMERGENCY", "OTHER"}

        if value not in allowed:
            raise ValueError(
                "closure_type must be HOLIDAY, EMERGENCY, or OTHER"
            )

        return value

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, value):
        if value is None:
            return None

        value = value.strip()

        if not value:
            return None

        return value

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
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Service name cannot be empty")

        return value

    @field_validator("duration_minutes")
    @classmethod
    def validate_duration(cls, value):
        if value <= 15:
            raise ValueError(
                "Duration must be greater than 15 minutes"
            )

        return value

    @field_validator("price_cents")
    @classmethod
    def validate_price(cls, value):
        if value < 0:
            raise ValueError(
                "Price cannot be negative"
            )

        return value

class BusinessHoursCreate(BaseModel):
    day_of_week: int
    open_time: Optional[time] = None
    close_time: Optional[time] = None
    is_closed: bool = False

    @field_validator("day_of_week")
    @classmethod
    def validate_day_of_week(cls, value):
        if value < 0 or value > 6:
            raise ValueError(
                "day_of_week must be between 0 and 6"
            )

        return value

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
    
    @model_validator(mode="after")
    def validate_hours(self):
        if self.is_closed:
            if self.open_time is not None or self.close_time is not None:
                raise ValueError(
                    "Closed days cannot have open or close times"
                )

            return self

        if self.open_time is None or self.close_time is None:
            raise ValueError(
                "Open and close times are required when business is open"
            )

        if self.close_time <= self.open_time:
            raise ValueError(
                "Close time must be after open time"
            )

        return self

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
    
    @model_validator(mode="after")
    def validate_hours(self):
        if self.is_off:
            if self.start_time is not None or self.end_time is not None:
                raise ValueError(
                    "Off days cannot have start or end times"
                )

            return self

        if self.start_time is None or self.end_time is None:
            raise ValueError(
                "Start and end times are required when barber is working"
            )

        if self.end_time <= self.start_time:
            raise ValueError(
                "End time must be after start time"
            )

        return self
    
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


class NotificationType(str, Enum):
    CONFIRMATION = "confirmation"
    RESCHEDULED = "rescheduled"
    CANCELLED = "cancelled"
    REMINDER = "reminder"


class NotificationChannel(str, Enum):
    SMS = "sms"
    EMAIL = "email"


class NotificationRecipientType(str, Enum):
    CUSTOMER = "customer"
    BARBER = "barber"
    SHOP = "shop"


class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    
class NotificationResponse(BaseModel):
    id: UUID
    appointment_id: UUID
    type: NotificationType
    channel: NotificationChannel
    recipient_type: NotificationRecipientType
    recipient_id: Optional[UUID] = None
    recipient: str
    message: str
    status: NotificationStatus
    scheduled_for: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime