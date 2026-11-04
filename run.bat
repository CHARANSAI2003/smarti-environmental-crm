@echo off
echo Setting up Smarti CRM environment...
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate
echo Installing dependencies...
pip install -r requirements.txt
echo Running database seeding...
python -m app.seed
echo Starting application on http://127.0.0.1:8000
python main.py
pause
