# apps/persistence.py
from sqlalchemy.orm import Session
from datetime import datetime, date 
from typing import List 
from database import models as dbmodels
from loggers.logger import get_logger
import pytz
logger = get_logger("persistence")




def create_doctor(db: Session, name: str, timezone: str, working_hours: dict) -> dbmodels.Doctor:
    logger.info("Creating doctor: %s", name)
    now = datetime.now(pytz.timezone(timezone or "Asia/Kolkata"))
    doc = dbmodels.Doctor(
        name=name,
        timezone=timezone,
        working_hours=working_hours,
        created_at=now,
        updated_at=now,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    logger.info("Created doctor id=%s name=%s", doc.id, name)
    return doc

def get_doctor(db: Session, doctor_id: int):
    return db.query(dbmodels.Doctor).filter(dbmodels.Doctor.id == doctor_id).first()

def list_doctors(db: Session) -> List[dbmodels.Doctor]:
    return db.query(dbmodels.Doctor).all()


def list_appointments_for_doctor_on_date(db: Session, doctor_id: int, target_date: date):
    start_of_day = datetime.combine(target_date, datetime.min.time()).astimezone()
    end_of_day = datetime.combine(target_date, datetime.max.time()).astimezone()
    return (
        db.query(dbmodels.Appointment)
        .filter(dbmodels.Appointment.doctor_id == doctor_id)
        .filter(dbmodels.Appointment.start_at >= start_of_day)
        .filter(dbmodels.Appointment.start_at <= end_of_day)
        .order_by(dbmodels.Appointment.start_at)
        .all()
    )

def list_appointments_for_doctor(db: Session, doctor_id: int):
    return (
        db.query(dbmodels.Appointment)
        .filter(dbmodels.Appointment.doctor_id == doctor_id)
        .order_by(dbmodels.Appointment.start_at)
        .all()
    )

def create_appointment(db: Session, doctor_id: int, start_at: datetime, end_at: datetime,
                       appt_type: str, patient_name: str = None, timezone: str = "Asia/Kolkata"):
    """
    Create an appointment and set created_at/updated_at using provided timezone (fallback to Asia/Kolkata).
    Signature order: (db, doctor_id, start_at, end_at, appt_type, patient_name=None, timezone=...)
    """
    logger.info("Creating appointment for doctor id=%s at %s", doctor_id, start_at)
    now = datetime.now(pytz.timezone(timezone or "Asia/Kolkata"))
    appt = dbmodels.Appointment(
        doctor_id=doctor_id,
        start_at=start_at,
        end_at=end_at,
        appt_type=appt_type,
        patient_name=patient_name,
        created_at=now,
        updated_at=now,
    )
    db.add(appt)
    db.commit()
    db.refresh(appt)
    logger.info("Created appointment id=%s doctor=%s start=%s", appt.id, doctor_id, start_at)
    return appt

def find_overlapping_appointments(db: Session, doctor_id: int, start_at: datetime, end_at: datetime):
    """
    Return any appointments that overlap [start_at, end_at)
    Overlap condition: start < existing.end_at and existing.start_at < end
    """
    return (
        db.query(dbmodels.Appointment)
        .filter(dbmodels.Appointment.doctor_id == doctor_id)
        .filter(dbmodels.Appointment.start_at < end_at)
        .filter(dbmodels.Appointment.end_at > start_at)
        .all()
    )
