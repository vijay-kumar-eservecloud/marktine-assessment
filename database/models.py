from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, Float,DateTime,JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    timezone = Column(String, nullable=False)
    working_hours = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=False)

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)

    # Appointment type: general, follow_up, physical, specialist
    appt_type = Column(String, nullable=False)

    # Appointment start & end times (timezone aware)
    start_at = Column(DateTime(timezone=True), nullable=False)
    end_at = Column(DateTime(timezone=True), nullable=False)

    patient_name = Column(String, nullable=True)

    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=False)
    
   