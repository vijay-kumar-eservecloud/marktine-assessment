# apps/routers.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from database.dependency import get_db
from sqlalchemy.orm import Session
from apps import models as appmodels
from apps import persistence, service
from database import models as dbmodels
from loggers.logger import get_logger
from datetime import datetime

logger = get_logger("api_router")
router = APIRouter()


@router.post("/doctors", response_model=appmodels.DoctorOut)
def create_doctor(payload: appmodels.DoctorCreate, db: Session = Depends(get_db)):
    logger.info("Creating doctor: %s", payload.name)
    doc = persistence.create_doctor(db, name=payload.name, timezone=payload.timezone, working_hours=payload.working_hours)
    logger.info("Created doctor with ID: %s", doc.id)
    return doc

@router.get("/doctors/{doctor_id}", response_model=appmodels.DoctorOut)
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    logger.info("Fetching doctor with ID: %s", doctor_id)
    doc = persistence.get_doctor(db, doctor_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Doctor not found")
    logger.info("Found doctor: %s", doc.name)
    return doc

@router.get("/doctors", response_model=List[appmodels.DoctorOut])
def list_doctors(db: Session = Depends(get_db)):
    return persistence.list_doctors(db)



@router.post("/available_slots", response_model=appmodels.AvailableSlotsResponse)
def available_slots(payload: appmodels.AvailableSlotsRequest, db: Session = Depends(get_db)):
    doc = persistence.get_doctor(db, payload.doctor_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Doctor not found")

    try:
        slots = service.compute_available_slots(db, doc, payload.date_iso, payload.appt_type, payload.timezone)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


    return {"slots": slots}


@router.post("/appointments", response_model=appmodels.AppointmentOut)
def create_appointment(payload: appmodels.AppointmentCreate, db: Session = Depends(get_db)):
    logger.info("Creating appointment for doctor ID: %s at %s", payload.doctor_id, payload.start_at.isoformat())
    doc = persistence.get_doctor(db, payload.doctor_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Doctor not found")
        

    # ensure start_at is timezone-aware
    if payload.start_at.tzinfo is None:
        raise HTTPException(status_code=400, detail="start_at must include timezone info (ISO offset)")

    try:
        appt = service.create_appointment_with_checks(db, doc, payload.start_at, payload.appt_type, payload.patient_name)
        logger.info("Created appointment ID: %s", appt.id)
    except ValueError as e:
        logger.error("Error creating appointment: %s", str(e))
        raise HTTPException(status_code=409 if "booked" in str(e).lower() else 400, detail=str(e))

    return appt


@router.get("/appointments/{doctor_id}", response_model=List[appmodels.AppointmentOut])
def list_appointments(doctor_id: int, db: Session = Depends(get_db), date_iso: str = None):
    logger.info("Listing appointments for doctor ID: %s", doctor_id)
    if date_iso:
        try:
            dt = datetime.fromisoformat(date_iso).date()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid date_iso")
        items = persistence.list_appointments_for_doctor_on_date(db, doctor_id, dt)
    else:
        items = persistence.list_appointments_for_doctor(db, doctor_id)
    logger.info("Found %s appointments", len(items))
    return items
