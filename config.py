import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CALENDLY_API_KEY = os.getenv("CALENDLY_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Business Rules
NEW_PATIENT_DURATION = 60  # minutes
RETURNING_PATIENT_DURATION = 30  # minutes

# File Paths
PATIENTS_CSV = "data/patients.csv"
DOCTORS_SCHEDULE_XLSX = "data/doctors_schedule.xlsx"
APPOINTMENTS_XLSX = "data/appointments.xlsx"
INTAKE_FORM_PDF = "forms/intake_form_template.pdf"

# Reminder Schedule (days before appointment)
REMINDER_SCHEDULE = [7, 3, 1]

# LLM Configuration
LLM_MODEL = "gpt-3.5-turbo"
LLM_TEMPERATURE = 0.1
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

# Streamlit Configuration
APP_TITLE = "AI Medical Scheduling Agent"
APP_DESCRIPTION = "Automated appointment scheduling with AI assistance"
