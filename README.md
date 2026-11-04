# Smarti Environmental — CRM & Job Management System

A production-ready, lightweight Customer Relationship Management (CRM) and field job dispatch prototype built for **Smarti Environmental Limited**.

The system manages customer onboarding, appointment booking, fitters, and maintenance engineers across commercial environmental water-efficiency projects.

---

## A. Getting Started

### Prerequisites
* **Python 3.10+** 
* **Pip** (Python package manager)

### 1. Setup Virtual Environment
Open a terminal (e.g. Command Prompt, PowerShell, or Bash) in the project folder:

```bash
# Create virtual environment
python -m venv venv

# Activate on Windows (CMD or PowerShell):
venv\Scripts\activate

# Or on macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize & Seed Database
The project utilizes a local SQLite database (`smarti.db`). To populate it with realistic commercial premises (Exeter Science Park, Marsh Barton, NHS hubs) and field engineers:
```bash
python -m app.seed
```
*(Note: If you run the server directly, it will also automatically create tables and seed demo data if the database is unpopulated).*

### 4. Run the Application
```bash
python main.py
```
*Alternatively, using Uvicorn directly:*
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### 5. Access the Web Application
Open your web browser and navigate to:
* **CRM Web App:** `http://127.0.0.1:8000`
* **Interactive API Documentation:** `http://127.0.0.1:8000/docs`

---

## B. Architecture & Design Decisions

### Technology Stack
* **Backend:** **FastAPI** (Python 3.10+). Chosen for low footprint, rapid development, native request validation with Pydantic, and automatic OpenAPI schema generation at `/docs`.
* **Database & ORM:** **SQLite with SQLAlchemy 2.0**. Requires zero external services or Docker setup for the reviewing panel, guaranteeing 1-command execution while maintaining relational integrity.
* **Frontend:** **Jinja2 server-rendered templates styled with Tailwind CSS (CDN)**. This eliminates Node.js/NPM bundling friction and build steps, ensuring instant compilation and high maintainability.

### Unified Appointments & Job Workflow
Rather than segregating "Appointments" and "Jobs" into disconnected tables, the system implements a unified relational model (`Job`):
* An appointment is a scheduled service visit linked to a Customer (`Customer` foreign key).
* A field specialist (`Staff` foreign key) is assigned directly to the appointment.
* The job tracks lifecycle progression: `Pending` → `In Progress` → `Completed`.

---

## C. Development Process & Reflection

1. **Schema & Relational Foundations:** Modeled `Customer`, `Staff`, and `Job` entities with foreign key cascades and relational mappings.
2. **Database Seeding (`seed.py`):** Established realistic initial data mirroring Smarti's environmental water operations.
3. **Core CRUD Implementation:** Built customer creation, status updates (`New Enquiry`, `In Progress`, `Active`), and appointment dispatch workflows.
4. **UI Refinement:** Implemented Tailwind CSS dashboard layout with KPI metrics and active schedule monitoring.

### 200-Word Assessment Summary
> Built a modular CRM and job management prototype using FastAPI, SQLite, and Tailwind CSS to manage customer onboarding and field engineer dispatching. Designed a unified workflow model linking commercial premises, engineering staff (fitters and maintenance technicians), and scheduled appointment slots with lifecycle tracking (`Pending` → `In Progress` → `Completed`).
> 
> I am most pleased with the friction-free developer experience and relational architecture: the application requires zero external database configurations, seeds instantly with realistic operational data, and auto-generates interactive OpenAPI documentation.
> 
> With additional time, I would implement calendar collision detection to prevent double-booking field engineers during overlapping time slots, add automated email/SMS status notifications for site contacts, and develop a dedicated mobile-responsive on-site check-in portal for engineers.
