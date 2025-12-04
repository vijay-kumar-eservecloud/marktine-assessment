# apps/service.py
from datetime import datetime, date, time, timedelta
from typing import List
import pytz

from apps import persistence
from loggers.logger import get_logger

logger = get_logger("service")

# appointment durations in minutes
APPT_DURATIONS = {
    "general": 30,
    "follow_up": 15,
    "physical": 45,
    "specialist": 60,
}


def parse_time_str(t: str) -> time:
    h, m = map(int, t.split(":"))
    return time(hour=h, minute=m)


def compute_available_slots(db, doctor, target_date: date, appt_type: str, tz_name: str = "Asia/Kolkata") -> List[datetime]:
    """
    Compute available start datetimes (timezone-aware) for the given doctor on target_date for appt_type.
    """
    if appt_type not in APPT_DURATIONS:
        raise ValueError("Unknown appointment type")

    duration_minutes = APPT_DURATIONS[appt_type]
    slot_delta = timedelta(minutes=duration_minutes)

    
    weekday = target_date.weekday()  # 0=Monday
    wh = None
    if doctor.working_hours:
        # JSON keys might be strings; convert to str index
        wh = doctor.working_hours.get(str(weekday)) or doctor.working_hours.get(weekday)

    if not wh:
        logger.info("No working hours for doctor %s on weekday %s", doctor.id, weekday)
        return []

    tz = pytz.timezone(tz_name or doctor.timezone or "Asia/Kolkata")
    start_time = parse_time_str(wh[0])
    end_time = parse_time_str(wh[1])

    start_dt = tz.localize(datetime.combine(target_date, start_time))
    end_dt = tz.localize(datetime.combine(target_date, end_time))

    # get existing appointments
    existing = persistence.list_appointments_for_doctor_on_date(db, doctor.id, target_date)
    existing_intervals = [(a.start_at.astimezone(tz), a.end_at.astimezone(tz)) for a in existing]

    slots = []
    cursor = start_dt
    while cursor + slot_delta <= end_dt:
        candidate_end = cursor + slot_delta
        conflict = False
        for s, e in existing_intervals:
            # overlap check
            if (cursor < e) and (s < candidate_end):
                conflict = True
                break
        if not conflict:
            slots.append(cursor)
        cursor = cursor + slot_delta

    return slots


def create_appointment_with_checks(db, doctor, start_at: datetime, appt_type: str, patient_name: str ):
    if appt_type not in APPT_DURATIONS:
        raise ValueError("Unknown appointment type")

    duration = timedelta(minutes=APPT_DURATIONS[appt_type])
    end_at = start_at + duration

    # check working hours containment
    weekday = start_at.date().weekday()
    wh = doctor.working_hours.get(str(weekday)) if doctor.working_hours else None
    if not wh:
        raise ValueError("Doctor not working that day")

    tz = pytz.timezone(doctor.timezone or "Asia/Kolkata")
    wh_start = tz.localize(datetime.combine(start_at.date(), parse_time_str(wh[0])))
    wh_end = tz.localize(datetime.combine(start_at.date(), parse_time_str(wh[1])))

    if not (wh_start <= start_at and end_at <= wh_end):
        raise ValueError("Appointment outside working hours")

    # overlap check
    overlapping = persistence.find_overlapping_appointments(db, doctor.id, start_at, end_at)
    if overlapping:
        raise ValueError("Slot already booked")

    # Create appointment
    appt = persistence.create_appointment(
    db,
    doctor.id,
    start_at,
    end_at,
    appt_type,
    patient_name,
    timezone=doctor.timezone
)
    return appt
