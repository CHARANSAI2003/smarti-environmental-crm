from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(120), nullable=False)
    phone = Column(String(40), nullable=False)
    address = Column(Text, nullable=False)
    onboarding_status = Column(String(40), default="New Enquiry")  # New Enquiry, In Progress, Active
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    jobs = relationship("Job", back_populates="customer", cascade="all, delete-orphan", order_by="desc(Job.scheduled_date)")

class Staff(Base):
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    role = Column(String(60), nullable=False)  # Fitter, Maintenance Engineer
    email = Column(String(120), nullable=False)
    phone = Column(String(40), nullable=False)
    specialism = Column(String(120), default="Water Systems & Sensors")
    is_active = Column(Integer, default=1)

    jobs = relationship("Job", back_populates="staff")

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=True)
    service_type = Column(String(100), nullable=False)
    scheduled_date = Column(String(20), nullable=False)  # YYYY-MM-DD
    scheduled_time = Column(String(10), nullable=False)  # HH:MM
    status = Column(String(30), default="Pending")       # Pending, In Progress, Completed
    location_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="jobs")
    staff = relationship("Staff", back_populates="jobs")
