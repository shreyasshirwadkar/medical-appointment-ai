# API Documentation - AI Medical Scheduling Agent

## Overview
This document provides comprehensive API documentation for the AI Medical Scheduling Agent system, including all agent interfaces, utility functions, and integration points.

---

## Core Agents

### 1. GreetingAgent

**Purpose**: Collect and validate patient information through natural language processing.

#### Methods

##### `process(user_input: str, collected_data: Dict[str, Any]) -> Dict[str, Any]`
Processes user input to extract patient information.

**Parameters:**
- `user_input`: User's conversational input
- `collected_data`: Previously collected patient information

**Returns:**
```python
{
    "message": str,              # AI response to user
    "extracted_data": dict,      # Extracted patient information
    "is_complete": bool,         # Whether all required fields are collected
    "missing_fields": list,      # List of missing required fields
    "next_step": str            # Next workflow step
}
```

**Required Fields:**
- `name`: Patient's full name
- `date_of_birth`: MM/DD/YYYY format
- `preferred_doctor`: Doctor preference
- `location`: Preferred clinic location

---

### 2. LookupAgent

**Purpose**: Search patient database and determine patient type (new/returning).

#### Methods

##### `process(patient_data: Dict[str, Any]) -> Dict[str, Any]`
Looks up patient in EMR system.

**Parameters:**
- `patient_data`: Patient information from greeting phase

**Returns:**
```python
{
    "message": str,                    # Response message
    "patient_type": str,               # "new" or "returning"
    "patient_id": str,                 # Unique patient identifier
    "patient_record": dict,            # Complete patient record
    "appointment_duration": int,       # 60 for new, 30 for returning
    "next_step": str                  # "scheduling"
}
```

##### `get_patient_history(patient_id: str) -> List[Dict]`
Retrieves complete appointment history for a patient.

---

### 3. SchedulingAgent

**Purpose**: Handle appointment scheduling and calendar integration.

#### Methods

##### `process(user_input: str, patient_data: Dict, appointment_data: Dict) -> Dict[str, Any]`
Process scheduling requests and manage appointments.

**Parameters:**
- `user_input`: User's scheduling preferences
- `patient_data`: Patient information
- `appointment_data`: Current appointment details

**Returns:**
```python
{
    "message": str,                    # Response message
    "available_slots": list,           # Available time slots
    "appointment_details": dict,       # Confirmed appointment data
    "booking_successful": bool,        # Booking status
    "next_step": str                  # Next workflow step
}
```

**Slot Format:**
```python
{
    "datetime": datetime,              # Appointment datetime
    "doctor": str,                     # Doctor name
    "location": str,                   # Clinic location
    "duration": int,                   # Appointment duration
    "available": bool                  # Availability status
}
```

---

### 4. InsuranceAgent

**Purpose**: Collect and validate insurance information.

#### Methods

##### `process(user_input: str, collected_insurance: Dict[str, Any]) -> Dict[str, Any]`
Extract insurance information from user input.

**Parameters:**
- `user_input`: User's insurance information
- `collected_insurance`: Previously collected insurance data

**Returns:**
```python
{
    "message": str,                    # Response message
    "extracted_insurance": dict,       # Extracted insurance data
    "is_complete": bool,              # Collection completion status
    "missing_fields": list,           # Missing required fields
    "next_step": str                  # Next workflow step
}
```

**Required Insurance Fields:**
- `insurance_carrier`: Insurance company name
- `member_id`: Member identification number
- `group_number`: Group number (optional)

##### `validate_insurance_info(insurance_data: Dict[str, Any]) -> Dict[str, Any]`
Validate insurance information format.

---

### 5. ReminderAgent

**Purpose**: Schedule and manage appointment reminders.

#### Methods

##### `schedule_reminders(appointment_data: Dict, patient_data: Dict) -> Dict[str, Any]`
Schedule all reminders for an appointment.

**Parameters:**
- `appointment_data`: Appointment details
- `patient_data`: Patient contact information

**Returns:**
```python
{
    "scheduled_reminders": list,       # List of scheduled reminders
    "total_reminders": int            # Total number of reminders
}
```

##### `send_reminder(reminder_data: Dict[str, Any]) -> Dict[str, Any]`
Send a specific reminder to the patient.

**Reminder Types:**
- `initial` (7 days): Basic appointment confirmation
- `form_check` (3 days): Intake form completion check
- `confirmation` (1 day): Final attendance confirmation

---

## Utility Services

### Database Class

#### Methods

##### `search_patient(name: str, dob: str) -> List[Dict]`
Search for existing patient records.

##### `create_patient_record(patient_data: Dict) -> str`
Create new patient record, returns patient ID.

##### `save_appointment(appointment_data: Dict) -> bool`
Save appointment to database.

##### `get_appointment(appointment_id: str) -> Dict`
Retrieve appointment by ID.

##### `get_patient(patient_id: str) -> Dict`
Retrieve patient record by ID.

---

### CalendarIntegration Class

#### Methods

##### `get_available_slots(doctor: str, location: str, duration: int, days_ahead: int) -> List[Dict]`
Get available appointment slots.

**Parameters:**
- `doctor`: Doctor name
- `location`: Clinic location
- `duration`: Appointment duration in minutes
- `days_ahead`: Number of days to look ahead

##### `book_appointment(selected_slot: Dict, appointment_details: Dict) -> bool`
Book an appointment slot.

##### `cancel_appointment(appointment_id: str) -> bool`
Cancel an existing appointment.

---

### EmailService Class

#### Methods

##### `send_confirmation_email(patient_data: Dict, appointment_data: Dict, insurance_data: Dict) -> bool`
Send appointment confirmation with intake forms.

##### `send_reminder_email(to_email: str, subject: str, message: str, appointment_data: Dict) -> bool`
Send appointment reminder email.

##### `send_form_completion_reminder(patient_email: str, patient_name: str, appointment_date: str) -> bool`
Send reminder to complete intake forms.

---

### SMSService Class

#### Methods

##### `send_reminder_sms(to_phone: str, message: str) -> bool`
Send SMS reminder to patient.

##### `send_appointment_confirmation_sms(patient_phone: str, patient_name: str, appointment_data: Dict) -> bool`
Send appointment confirmation SMS.

##### `process_sms_response(from_phone: str, message: str) -> Dict[str, Any]`
Process incoming SMS responses from patients.

---

### ExcelExporter Class

#### Methods

##### `export_appointment(patient_data: Dict, appointment_data: Dict, insurance_data: Dict) -> str`
Export single appointment to Excel file.

##### `export_daily_appointments(date: datetime) -> str`
Export all appointments for a specific date.

##### `export_patient_history(patient_id: str) -> str`
Export complete appointment history for a patient.

##### `export_monthly_report(year: int, month: int) -> str`
Generate comprehensive monthly report.

---

## Data Structures

### Patient Record
```python
{
    "patient_id": str,              # Unique identifier
    "name": str,                    # Full name
    "date_of_birth": str,           # MM/DD/YYYY
    "email": str,                   # Email address
    "phone": str,                   # Phone number
    "preferred_doctor": str,        # Doctor preference
    "location": str,                # Preferred location
    "first_visit": str,             # YYYY-MM-DD
    "usual_doctor": str,            # Regular doctor
    "insurance_carrier": str,       # Insurance company
    "member_id": str,               # Insurance member ID
    "group_number": str             # Insurance group number
}
```

### Appointment Record
```python
{
    "appointment_id": str,          # Unique identifier
    "patient_id": str,              # Patient reference
    "doctor": str,                  # Doctor name
    "datetime": datetime,           # Appointment datetime
    "duration": int,                # Duration in minutes
    "location": str,                # Clinic location
    "status": str,                  # "confirmed", "cancelled"
    "created_at": datetime          # Creation timestamp
}
```

### Reminder Record
```python
{
    "reminder_id": str,             # Unique identifier
    "appointment_id": str,          # Appointment reference
    "patient_id": str,              # Patient reference
    "reminder_datetime": datetime,   # When to send reminder
    "days_before": int,             # Days before appointment
    "type": str,                    # Reminder type
    "status": str,                  # "scheduled", "sent"
    "response": str                 # Patient response
}
```

---

## Error Handling

### Common Error Responses
```python
{
    "success": bool,                # Operation success status
    "error": str,                   # Error message
    "error_code": str,              # Error classification
    "retry_allowed": bool           # Whether retry is possible
}
```

### Error Codes
- `PATIENT_NOT_FOUND`: Patient record not found
- `APPOINTMENT_CONFLICT`: Time slot conflict
- `INVALID_INPUT`: Invalid user input format
- `EXTERNAL_SERVICE_ERROR`: Third-party service failure
- `VALIDATION_ERROR`: Data validation failure

---

## Configuration

### Environment Variables
```bash
OPENAI_API_KEY=your_openai_api_key
CALENDLY_API_KEY=your_calendly_api_key
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_email_password
```

### Business Rules Configuration
```python
NEW_PATIENT_DURATION = 60          # Minutes
RETURNING_PATIENT_DURATION = 30    # Minutes
REMINDER_SCHEDULE = [7, 3, 1]       # Days before appointment
LLM_MODEL = "gpt-3.5-turbo"
LLM_TEMPERATURE = 0.1
```

---

## Testing

### Sample Test Data
The system includes 50 synthetic patient records and 5 doctor schedules for comprehensive testing.

### Test Scenarios
1. New patient booking workflow
2. Returning patient scheduling
3. Insurance information collection
4. Reminder system functionality
5. Calendar conflict resolution
6. Form distribution and tracking

---

**API Version:** 1.0  
**Last Updated:** September 5, 2025
