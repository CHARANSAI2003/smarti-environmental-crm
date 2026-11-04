from datetime import datetime, timezone, date
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session
from app import models

def get_now_gmt():
    """Returns the current datetime in GMT / UTC."""
    return datetime.now(timezone.utc)

def get_customers(db: Session, search: str = None, status: str = None):
    query = db.query(models.Customer)
    if search:
        s = f"%{search.strip()}%"
        query = query.filter(
            (models.Customer.name.ilike(s)) |
            (models.Customer.email.ilike(s)) |
            (models.Customer.address.ilike(s))
        )
    if status and status != "All":
        query = query.filter(models.Customer.onboarding_status == status)
    return query.order_by(models.Customer.id.desc()).all()

def get_customer(db: Session, customer_id: int):
    return db.query(models.Customer).filter(models.Customer.id == customer_id).first()

def create_customer(db: Session, name: str, email: str, phone: str, address: str, onboarding_status: str, notes: str = None):
    customer = models.Customer(
        name=name.strip(),
        email=email.strip(),
        phone=phone.strip(),
        address=address.strip(),
        onboarding_status=onboarding_status,
        notes=notes.strip() if notes else ""
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer

def update_customer(db: Session, customer_id: int, name: str, email: str, phone: str, address: str, onboarding_status: str, notes: str = None):
    customer = get_customer(db, customer_id)
    if customer:
        customer.name = name.strip()
        customer.email = email.strip()
        customer.phone = phone.strip()
        customer.address = address.strip()
        customer.onboarding_status = onboarding_status
        if notes is not None:
            customer.notes = notes.strip()
        db.commit()
        db.refresh(customer)
    return customer

def get_staff_members(db: Session):
    return db.query(models.Staff).filter(models.Staff.is_active == 1).order_by(models.Staff.name.asc()).all()

def get_staff(db: Session, staff_id: int):
    return db.query(models.Staff).filter(models.Staff.id == staff_id).first()

def create_staff(db: Session, name: str, role: str, email: str, phone: str, specialism: str = None):
    staff = models.Staff(
        name=name.strip(),
        role=role.strip(),
        email=email.strip(),
        phone=phone.strip(),
        specialism=specialism.strip() if specialism else "Water Efficiency & Sensor Maintenance"
    )
    db.add(staff)
    db.commit()
    db.refresh(staff)
    return staff

def get_jobs(db: Session, status: str = None, view: str = None):
    query = db.query(models.Job)
    now_gmt = get_now_gmt()
    today_str = now_gmt.strftime("%Y-%m-%d")
    current_time_str = now_gmt.strftime("%H:%M")

    if view == "upcoming":
        # Must be future date OR today with time >= current GMT time OR active In Progress
        query = query.filter(
            models.Job.status.in_(["Pending", "In Progress"]),
            or_(
                models.Job.scheduled_date > today_str,
                and_(models.Job.scheduled_date == today_str, models.Job.scheduled_time >= current_time_str),
                and_(models.Job.scheduled_date == today_str, models.Job.status == "In Progress")
            )
        )
        return query.order_by(models.Job.scheduled_date.asc(), models.Job.scheduled_time.asc()).all()

    elif view == "completed":
        query = query.filter(models.Job.status == "Completed")
        return query.order_by(models.Job.scheduled_date.desc(), models.Job.scheduled_time.desc()).all()

    if status and status != "All":
        query = query.filter(models.Job.status == status)

    return query.order_by(models.Job.scheduled_date.desc(), models.Job.scheduled_time.desc()).all()

def get_upcoming_jobs(db: Session, limit: int = None):
    now_gmt = get_now_gmt()
    today_str = now_gmt.strftime("%Y-%m-%d")
    current_time_str = now_gmt.strftime("%H:%M")

    query = db.query(models.Job).filter(
        models.Job.status.in_(["Pending", "In Progress"]),
        or_(
            models.Job.scheduled_date > today_str,
            and_(models.Job.scheduled_date == today_str, models.Job.scheduled_time >= current_time_str),
            and_(models.Job.scheduled_date == today_str, models.Job.status == "In Progress")
        )
    ).order_by(models.Job.scheduled_date.asc(), models.Job.scheduled_time.asc())

    if limit:
        query = query.limit(limit)
    return query.all()

def get_completed_jobs(db: Session, limit: int = None):
    query = db.query(models.Job).filter(
        models.Job.status == "Completed"
    ).order_by(models.Job.scheduled_date.desc(), models.Job.scheduled_time.desc())
    if limit:
        query = query.limit(limit)
    return query.all()

def get_job(db: Session, job_id: int):
    return db.query(models.Job).filter(models.Job.id == job_id).first()

def create_job(db: Session, customer_id: int, staff_id: int, service_type: str, scheduled_date: str, scheduled_time: str, location_notes: str = None, status: str = "Pending"):
    job = models.Job(
        customer_id=customer_id,
        staff_id=staff_id if staff_id and staff_id > 0 else None,
        service_type=service_type.strip(),
        scheduled_date=scheduled_date.strip(),
        scheduled_time=scheduled_time.strip(),
        status=status,
        location_notes=location_notes.strip() if location_notes else ""
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

def update_job(db: Session, job_id: int, customer_id: int, staff_id: int, service_type: str, scheduled_date: str, scheduled_time: str, status: str, location_notes: str = None):
    job = get_job(db, job_id)
    if job:
        job.customer_id = customer_id
        job.staff_id = staff_id if staff_id and staff_id > 0 else None
        job.service_type = service_type.strip()
        job.scheduled_date = scheduled_date.strip()
        job.scheduled_time = scheduled_time.strip()
        job.status = status
        if location_notes is not None:
            job.location_notes = location_notes.strip()
        db.commit()
        db.refresh(job)
    return job