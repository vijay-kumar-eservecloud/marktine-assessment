# apps/models.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from enum import Enum

# ---------- Doctors ----------
class DoctorCreate(BaseModel):
    name: str
    timezone: Optional[str] = "Asia/Kolkata"
    working_hours: dict  # weekday -> [start, end], e.g. {"0": ["09:00","17:00"]}

class DoctorOut(BaseModel):
    id: int
    name: str
    timezone: str
    working_hours: dict
    is_active: bool

    class Config:
        orm_mode = True

# ---------- Appointment ----------

class AppointmentTypeEnum(str, Enum):
    general = "general"
    follow_up = "follow_up"
    physical = "physical"
    specialist = "specialist"

class AppointmentCreate(BaseModel):
    doctor_id: int
    start_at: datetime
    appt_type: str = AppointmentTypeEnum
    patient_name: Optional[str] = None

class AppointmentOut(BaseModel):
    id: int
    doctor_id: int
    appt_type: str
    start_at: datetime
    end_at: datetime
    patient_name: Optional[str]

    class Config:
        orm_mode = True

# ---------- Available slots request ----------
class AvailableSlotsRequest(BaseModel):
    doctor_id: int
    date_iso: date
    appt_type: str
    timezone: Optional[str] = "Asia/Kolkata"

class AvailableSlotsResponse(BaseModel):
    slots: List[datetime]
