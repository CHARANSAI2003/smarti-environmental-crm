import os
from datetime import datetime, timezone, timedelta
from fastapi import FastAPI, Depends, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import engine, get_db, Base
from app import models, crud
from app.seed import seed_data

Base.metadata.create_all(bind=engine)
seed_data()

app = FastAPI(title="Smarti Environmental - CRM & Job Management System")
templates = Jinja2Templates(directory="app/templates")

DISPATCH_SLOTS = [
    {"time": "08:30", "label": "08:30 - 10:00", "period": "Early Morning"},
    {"time": "10:00", "label": "10:00 - 11:30", "period": "Mid Morning"},
    {"time": "11:30", "label": "11:30 - 13:00", "period": "Midday"},
    {"time": "13:30", "label": "13:30 - 15:00", "period": "Early Afternoon"},
    {"time": "15:00", "label": "15:00 - 16:30", "period": "Late Afternoon"},
    {"time": "16:30", "label": "16:30 - 18:00", "period": "End of Day Dispatch"}
]

def get_gmt_time_context():
    """Helper returning standard GMT time parameters & smart defaults."""
    now_gmt = datetime.now(timezone.utc)
    today_gmt = now_gmt.strftime("%Y-%m-%d")
    now_gmt_time = now_gmt.strftime("%H:%M")
    
    # Find next available slot today
    available_today = [s for s in DISPATCH_SLOTS if s["time"] > now_gmt_time]
    
    if available_today:
        suggested_date = today_gmt
        suggested_slot_time = available_today[0]["time"]
    else:
        # If all slots passed today (e.g. late evening or night), default to tomorrow at 08:30
        suggested_date = (now_gmt + timedelta(days=1)).strftime("%Y-%m-%d")
        suggested_slot_time = "08:30"
        
    return {
        "today_gmt": today_gmt,
        "now_gmt_time": now_gmt_time,
        "suggested_date": suggested_date,
        "suggested_slot_time": suggested_slot_time,
        "dispatch_slots": DISPATCH_SLOTS
    }

@app.get("/", response_class=HTMLResponse)
def view_dashboard(request: Request, db: Session = Depends(get_db)):
    customers = crud.get_customers(db)
    staff = crud.get_staff_members(db)
    
    upcoming_jobs = crud.get_upcoming_jobs(db, limit=5)
    completed_jobs = crud.get_completed_jobs(db, limit=5)
    completed_jobs_count = len(crud.get_completed_jobs(db))

    active_customers = sum(1 for c in customers if c.onboarding_status == "Active")
    in_progress_customers = sum(1 for c in customers if c.onboarding_status == "In Progress")
    new_enquiries = sum(1 for c in customers if c.onboarding_status == "New Enquiry")

    time_ctx = get_gmt_time_context()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "active_page": "dashboard",
            "customers": customers,
            "staff": staff,
            "upcoming_jobs": upcoming_jobs,
            "completed_jobs": completed_jobs,
            "active_customers": active_customers,
            "in_progress_customers": in_progress_customers,
            "new_enquiries": new_enquiries,
            "completed_jobs_count": completed_jobs_count,
            "today_gmt": time_ctx["today_gmt"],
            "now_gmt_time": time_ctx["now_gmt_time"]
        }
    )

@app.get("/customers", response_class=HTMLResponse)
def list_customers(request: Request, search: str = None, status: str = None, db: Session = Depends(get_db)):
    customers = crud.get_customers(db, search=search, status=status)
    return templates.TemplateResponse(
        request=request,
        name="customers.html",
        context={
            "active_page": "customers",
            "customers": customers,
            "search_query": search,
            "selected_status": status or "All"
        }
    )

@app.get("/customers/new", response_class=HTMLResponse)
def new_customer_form(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="customer_edit.html",
        context={"active_page": "customers", "customer": None}
    )

@app.post("/customers/new")
def create_customer_action(
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    address: str = Form(...),
    onboarding_status: str = Form("New Enquiry"),
    notes: str = Form(""),
    db: Session = Depends(get_db)
):
    crud.create_customer(db, name, email, phone, address, onboarding_status, notes)
    return RedirectResponse(url="/customers", status_code=303)

@app.get("/customers/{customer_id}", response_class=HTMLResponse)
def view_customer(request: Request, customer_id: int, db: Session = Depends(get_db)):
    customer = crud.get_customer(db, customer_id)
    if not customer:
        return RedirectResponse(url="/customers")
    return templates.TemplateResponse(
        request=request,
        name="customer_detail.html",
        context={"active_page": "customers", "customer": customer}
    )

@app.get("/customers/{customer_id}/edit", response_class=HTMLResponse)
def edit_customer_form(request: Request, customer_id: int, db: Session = Depends(get_db)):
    customer = crud.get_customer(db, customer_id)
    if not customer:
        return RedirectResponse(url="/customers")
    return templates.TemplateResponse(
        request=request,
        name="customer_edit.html",
        context={"active_page": "customers", "customer": customer}
    )

@app.post("/customers/{customer_id}/edit")
def update_customer_action(
    customer_id: int,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    address: str = Form(...),
    onboarding_status: str = Form(...),
    notes: str = Form(""),
    db: Session = Depends(get_db)
):
    crud.update_customer(db, customer_id, name, email, phone, address, onboarding_status, notes)
    return RedirectResponse(url=f"/customers/{customer_id}", status_code=303)

@app.post("/customers/{customer_id}/status")
def update_customer_status_quick(customer_id: int, onboarding_status: str = Form(...), db: Session = Depends(get_db)):
    customer = crud.get_customer(db, customer_id)
    if customer:
        customer.onboarding_status = onboarding_status
        db.commit()
    return RedirectResponse(url="/customers", status_code=303)

@app.get("/jobs", response_class=HTMLResponse)
def list_jobs(request: Request, view: str = "upcoming", status: str = None, db: Session = Depends(get_db)):
    jobs = crud.get_jobs(db, status=status, view=view)
    time_ctx = get_gmt_time_context()
    return templates.TemplateResponse(
        request=request,
        name="jobs.html",
        context={
            "active_page": "jobs",
            "jobs": jobs,
            "current_view": view,
            "selected_status": status or "All",
            "now_gmt_time": time_ctx["now_gmt_time"]
        }
    )

@app.get("/jobs/new", response_class=HTMLResponse)
def new_job_form(request: Request, customer_id: int = None, db: Session = Depends(get_db)):
    customers = crud.get_customers(db)
    staff = crud.get_staff_members(db)
    time_ctx = get_gmt_time_context()
    
    return templates.TemplateResponse(
        request=request,
        name="job_edit.html",
        context={
            "active_page": "jobs",
            "job": None,
            "customers": customers,
            "staff": staff,
            "selected_customer_id": customer_id,
            "today_gmt": time_ctx["today_gmt"],
            "now_gmt_time": time_ctx["now_gmt_time"],
            "suggested_date": time_ctx["suggested_date"],
            "selected_slot_time": time_ctx["suggested_slot_time"],
            "dispatch_slots": time_ctx["dispatch_slots"],
            "error_message": None
        }
    )

@app.post("/jobs/new")
def create_job_action(
    request: Request,
    customer_id: int = Form(...),
    staff_id: int = Form(0),
    service_type: str = Form(...),
    scheduled_date: str = Form(...),
    scheduled_time: str = Form(...),
    location_notes: str = Form(""),
    status: str = Form("Pending"),
    db: Session = Depends(get_db)
):
    time_ctx = get_gmt_time_context()
    today_gmt = time_ctx["today_gmt"]
    now_gmt_time = time_ctx["now_gmt_time"]

    # Strict server validation: prevent past dates or past slots today
    is_past_date = scheduled_date < today_gmt
    is_past_slot_today = (scheduled_date == today_gmt and scheduled_time <= now_gmt_time)

    if (is_past_date or is_past_slot_today) and status != "Completed":
        customers = crud.get_customers(db)
        staff = crud.get_staff_members(db)
        return templates.TemplateResponse(
            request=request,
            name="job_edit.html",
            context={
                "active_page": "jobs",
                "job": None,
                "customers": customers,
                "staff": staff,
                "selected_customer_id": customer_id,
                "today_gmt": today_gmt,
                "now_gmt_time": now_gmt_time,
                "suggested_date": time_ctx["suggested_date"],
                "selected_slot_time": time_ctx["suggested_slot_time"],
                "dispatch_slots": time_ctx["dispatch_slots"],
                "form_service_type": service_type,
                "form_date": scheduled_date,
                "form_notes": location_notes,
                "error_message": f"Dispatch slot '{scheduled_time}' on {scheduled_date} is already closed/passed (Current GMT is {now_gmt_time}). Please choose an upcoming slot."
            }
        )

    crud.create_job(db, customer_id, staff_id, service_type, scheduled_date, scheduled_time, location_notes, status)
    return RedirectResponse(url="/jobs?view=upcoming", status_code=303)

@app.get("/jobs/{job_id}/edit", response_class=HTMLResponse)
def edit_job_form(request: Request, job_id: int, db: Session = Depends(get_db)):
    job = crud.get_job(db, job_id)
    if not job:
        return RedirectResponse(url="/jobs")
    customers = crud.get_customers(db)
    staff = crud.get_staff_members(db)
    time_ctx = get_gmt_time_context()
    
    return templates.TemplateResponse(
        request=request,
        name="job_edit.html",
        context={
            "active_page": "jobs",
            "job": job,
            "customers": customers,
            "staff": staff,
            "selected_customer_id": job.customer_id,
            "today_gmt": time_ctx["today_gmt"],
            "now_gmt_time": time_ctx["now_gmt_time"],
            "suggested_date": time_ctx["suggested_date"],
            "selected_slot_time": job.scheduled_time,
            "dispatch_slots": time_ctx["dispatch_slots"],
            "error_message": None
        }
    )

@app.post("/jobs/{job_id}/edit")
def update_job_action(
    job_id: int,
    customer_id: int = Form(...),
    staff_id: int = Form(0),
    service_type: str = Form(...),
    scheduled_date: str = Form(...),
    scheduled_time: str = Form(...),
    status: str = Form("Pending"),
    location_notes: str = Form(""),
    db: Session = Depends(get_db)
):
    crud.update_job(db, job_id, customer_id, staff_id, service_type, scheduled_date, scheduled_time, status, location_notes)
    return RedirectResponse(url="/jobs", status_code=303)

@app.post("/jobs/{job_id}/status")
def update_job_status_quick(job_id: int, status: str = Form(...), db: Session = Depends(get_db)):
    job = crud.get_job(db, job_id)
    if job:
        job.status = status
        db.commit()
    return RedirectResponse(url="/jobs", status_code=303)

@app.get("/staff", response_class=HTMLResponse)
def list_staff(request: Request, db: Session = Depends(get_db)):
    staff = crud.get_staff_members(db)
    return templates.TemplateResponse(
        request=request,
        name="staff.html",
        context={"active_page": "staff", "staff": staff}
    )

@app.post("/staff/new")
def create_staff_action(
    name: str = Form(...),
    role: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    specialism: str = Form(""),
    db: Session = Depends(get_db)
):
    crud.create_staff(db, name, role, email, phone, specialism)
    return RedirectResponse(url="/staff", status_code=303)

if __name__ == "__main__":
    import uvicorn
    print("Starting Smarti Environmental CRM on http://127.0.0.1:8000 ...")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)