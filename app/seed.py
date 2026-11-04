from app.database import SessionLocal, engine
from app import models

def seed_data():
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Check if data already exists
    if db.query(models.Staff).first():
        print("Data already present in database. Skipping seeding.")
        db.close()
        return

    print("Seeding initial realistic operational data...")

    # 1. Staff Members (Fitters & Maintenance Engineers)
    staff_list = [
        models.Staff(name="David Miller", role="Fitter", email="d.miller@smartilimited.com", phone="07700 900111", specialism="Urinal Valve Retrofit & Pipework"),
        models.Staff(name="Sarah Jenkins", role="Maintenance Engineer", email="s.jenkins@smartilimited.com", phone="07700 900222", specialism="IoT Telemetry & Flow Metrology"),
        models.Staff(name="Marcus Vance", role="Fitter", email="m.vance@smartilimited.com", phone="07700 900333", specialism="Commercial Washrooms & Hydraulics"),
        models.Staff(name="Elena Rostova", role="Maintenance Engineer", email="e.rostova@smartilimited.com", phone="07700 900444", specialism="Acoustic Leak Detection & Pressure Audits")
    ]
    db.add_all(staff_list)
    db.commit()

    # 2. Customers across various onboarding stages
    customers_list = [
        models.Customer(
            name="Apex Tech Hub",
            email="facilities@apextech.co.uk",
            phone="01392 400100",
            address="Building 4, Exeter Science Park, Babbage Way, Exeter EX5 2FN",
            onboarding_status="Active",
            notes="Eco-audit completed. Smart valves deployed across all 4 storeys."
        ),
        models.Customer(
            name="Greenwood Leisure & Spa",
            email="operations@greenwoodleisure.co.uk",
            phone="01392 400200",
            address="18 Haldon Hill, Kennford, Exeter EX6 7YJ",
            onboarding_status="In Progress",
            notes="Pilot approved for locker rooms. Waiting for initial water meter logs."
        ),
        models.Customer(
            name="Beacon Logistics Centre",
            email="estates@beaconlogistics.com",
            phone="01392 400300",
            address="Unit 7, Marsh Barton Trading Estate, Exeter EX2 8PY",
            onboarding_status="New Enquiry",
            notes="Enquiry via web form. Needs site survey on 12 commercial urinals."
        ),
        models.Customer(
            name="Pinhoe Medical Centre",
            email="practice.manager@pinhoemedical.nhs.uk",
            phone="01392 400400",
            address="Pinhoe Road, Exeter EX4 8EG",
            onboarding_status="Active",
            notes="NHS sustainability grant recipient. Annual maintenance schedule in place."
        )
    ]
    db.add_all(customers_list)
    db.commit()

    # 3. Scheduled Jobs / Appointments
    jobs_list = [
        models.Job(
            customer_id=1,
            staff_id=1,
            service_type="Smart Valve Calibration & Sensor Retrofit",
            scheduled_date="2026-11-06",
            scheduled_time="09:00",
            status="In Progress",
            location_notes="Main washroom block on 2nd floor. Security pass required at front desk."
        ),
        models.Job(
            customer_id=2,
            staff_id=2,
            service_type="Acoustic Leak Detection & Pilot Survey",
            scheduled_date="2026-11-09",
            scheduled_time="11:30",
            status="Pending",
            location_notes="Speak with Operations Manager (Mike) at reception."
        ),
        models.Job(
            customer_id=3,
            staff_id=3,
            service_type="Initial Premises Site Survey & Flow Audit",
            scheduled_date="2026-11-12",
            scheduled_time="14:00",
            status="Pending",
            location_notes="High-vis jacket and safety boots mandatory for logistics warehouse."
        ),
        models.Job(
            customer_id=4,
            staff_id=4,
            service_type="Routine Annual Compliance & Gateway Check",
            scheduled_date="2026-11-02",
            scheduled_time="10:00",
            status="Completed",
            location_notes="Complete sensor battery checks and verify cloud telemetry upload."
        )
    ]
    db.add_all(jobs_list)
    db.commit()
    db.close()
    print("Database successfully populated with Smarti Environmental records.")

if __name__ == "__main__":
    seed_data()
