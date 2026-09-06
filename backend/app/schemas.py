from pydantic import BaseModel
from typing import Optional

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


class ServiceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    duration_minutes: int
    price_cents: int