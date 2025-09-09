import pandas as pd
import uuid
from datetime import datetime, timedelta
import random

def generate_sample_patients(num_patients=50):
    """Generate sample patient data for testing."""
    
    # Sample data lists
    first_names = [
        'John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Robert', 'Jessica', 
        'William', 'Ashley', 'Christopher', 'Amanda', 'Matthew', 'Stephanie', 'James',
        'Jennifer', 'Daniel', 'Nicole', 'Andrew', 'Elizabeth', 'Joshua', 'Heather',
        'Ryan', 'Samantha', 'Nicholas', 'Rachel', 'Joseph', 'Amy', 'Tyler', 'Angela',
        'Brandon', 'Brenda', 'Gregory', 'Emma', 'Alexander', 'Olivia', 'Patrick',
        'Kimberly', 'Jack', 'Lisa', 'Dennis', 'Betty', 'Jerry', 'Dorothy', 'Tyler',
        'Helen', 'Aaron', 'Sandra', 'Jose', 'Donna'
    ]
    
    last_names = [
        'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
        'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzales', 'Wilson', 'Anderson',
        'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson',
        'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson',
        'Walker', 'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen',
        'Hill', 'Flores', 'Green', 'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera',
        'Campbell', 'Mitchell', 'Carter', 'Roberts'
    ]
    
    doctors = ['Smith', 'Johnson', 'Wilson', 'Davis', 'Brown']
    locations = ['Downtown', 'Uptown', 'Midtown', 'Westside', 'Eastside']
    insurance_carriers = [
        'Aetna', 'Blue Cross Blue Shield', 'Cigna', 'Humana', 'United Healthcare',
        'Kaiser Permanente', 'Anthem', 'Medicare', 'Medicaid'
    ]
    
    patients = []
    
    for i in range(num_patients):
        # Generate patient data
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        
        # Generate realistic DOB (ages 18-80)
        age = random.randint(18, 80)
        birth_date = datetime.now() - timedelta(days=age*365 + random.randint(0, 365))
        
        # Generate first visit date (some new, some returning)
        if i < 10:  # First 10 are new patients
            first_visit = datetime.now().date()
        else:  # Rest are returning patients
            days_ago = random.randint(30, 1825)  # 1 month to 5 years ago
            first_visit = (datetime.now() - timedelta(days=days_ago)).date()
        
        patient = {
            'patient_id': str(uuid.uuid4())[:8],
            'name': f"{first_name} {last_name}",
            'date_of_birth': birth_date.strftime('%m/%d/%Y'),
            'email': f"{first_name.lower()}.{last_name.lower()}@email.com",
            'phone': f"({random.randint(200,999)}) {random.randint(200,999)}-{random.randint(1000,9999)}",
            'preferred_doctor': random.choice(doctors),
            'location': random.choice(locations),
            'first_visit': first_visit.strftime('%Y-%m-%d'),
            'usual_doctor': random.choice(doctors),
            'insurance_carrier': random.choice(insurance_carriers),
            'member_id': f"{random.randint(100000000,999999999)}",
            'group_number': f"{random.randint(10000,99999)}" if random.random() > 0.3 else ""
        }
        
        patients.append(patient)
    
    # Create DataFrame and save to CSV
    patients_df = pd.DataFrame(patients)
    patients_df.to_csv('data/patients.csv', index=False)
    print(f"Generated {num_patients} sample patients in data/patients.csv")
    
    return patients_df

def generate_doctors_schedule():
    """Generate doctors schedule data."""
    
    doctors_schedule = [
        # Dr. Smith - Downtown
        {"doctor": "Smith", "location": "Downtown", "weekday": "Monday", "start_time": "09:00", "end_time": "17:00"},
        {"doctor": "Smith", "location": "Downtown", "weekday": "Tuesday", "start_time": "09:00", "end_time": "17:00"},
        {"doctor": "Smith", "location": "Downtown", "weekday": "Wednesday", "start_time": "09:00", "end_time": "17:00"},
        {"doctor": "Smith", "location": "Downtown", "weekday": "Thursday", "start_time": "09:00", "end_time": "17:00"},
        {"doctor": "Smith", "location": "Downtown", "weekday": "Friday", "start_time": "09:00", "end_time": "15:00"},
        
        # Dr. Johnson - Uptown
        {"doctor": "Johnson", "location": "Uptown", "weekday": "Monday", "start_time": "08:00", "end_time": "16:00"},
        {"doctor": "Johnson", "location": "Uptown", "weekday": "Tuesday", "start_time": "08:00", "end_time": "16:00"},
        {"doctor": "Johnson", "location": "Uptown", "weekday": "Wednesday", "start_time": "08:00", "end_time": "16:00"},
        {"doctor": "Johnson", "location": "Uptown", "weekday": "Thursday", "start_time": "08:00", "end_time": "16:00"},
        {"doctor": "Johnson", "location": "Uptown", "weekday": "Friday", "start_time": "08:00", "end_time": "14:00"},
        
        # Dr. Wilson - Midtown
        {"doctor": "Wilson", "location": "Midtown", "weekday": "Monday", "start_time": "10:00", "end_time": "18:00"},
        {"doctor": "Wilson", "location": "Midtown", "weekday": "Tuesday", "start_time": "10:00", "end_time": "18:00"},
        {"doctor": "Wilson", "location": "Midtown", "weekday": "Wednesday", "start_time": "10:00", "end_time": "18:00"},
        {"doctor": "Wilson", "location": "Midtown", "weekday": "Thursday", "start_time": "10:00", "end_time": "18:00"},
        {"doctor": "Wilson", "location": "Midtown", "weekday": "Friday", "start_time": "10:00", "end_time": "16:00"},
        
        # Dr. Davis - Westside
        {"doctor": "Davis", "location": "Westside", "weekday": "Monday", "start_time": "09:30", "end_time": "17:30"},
        {"doctor": "Davis", "location": "Westside", "weekday": "Tuesday", "start_time": "09:30", "end_time": "17:30"},
        {"doctor": "Davis", "location": "Westside", "weekday": "Wednesday", "start_time": "09:30", "end_time": "17:30"},
        {"doctor": "Davis", "location": "Westside", "weekday": "Thursday", "start_time": "09:30", "end_time": "17:30"},
        {"doctor": "Davis", "location": "Westside", "weekday": "Friday", "start_time": "09:30", "end_time": "15:30"},
        
        # Dr. Brown - Eastside
        {"doctor": "Brown", "location": "Eastside", "weekday": "Monday", "start_time": "08:30", "end_time": "16:30"},
        {"doctor": "Brown", "location": "Eastside", "weekday": "Tuesday", "start_time": "08:30", "end_time": "16:30"},
        {"doctor": "Brown", "location": "Eastside", "weekday": "Wednesday", "start_time": "08:30", "end_time": "16:30"},
        {"doctor": "Brown", "location": "Eastside", "weekday": "Thursday", "start_time": "08:30", "end_time": "16:30"},
        {"doctor": "Brown", "location": "Eastside", "weekday": "Friday", "start_time": "08:30", "end_time": "14:30"},
    ]
    
    # Save to Excel
    schedule_df = pd.DataFrame(doctors_schedule)
    schedule_df.to_excel('data/doctors_schedule.xlsx', index=False)
    print("Generated doctors schedule in data/doctors_schedule.xlsx")
    
    return schedule_df

def initialize_appointments_file():
    """Initialize empty appointments file."""
    
    appointments_df = pd.DataFrame(columns=[
        'appointment_id', 'patient_id', 'doctor', 'datetime',
        'duration', 'location', 'status', 'created_at'
    ])
    appointments_df.to_excel('data/appointments.xlsx', index=False)
    print("Initialized empty appointments file in data/appointments.xlsx")

if __name__ == "__main__":
    # Generate all sample data
    print("Generating sample data for AI Scheduling Agent...")
    
    generate_sample_patients(50)
    generate_doctors_schedule()
    initialize_appointments_file()
    
    print("Sample data generation complete!")
    print("Files created:")
    print("- data/patients.csv (50 sample patients)")
    print("- data/doctors_schedule.xlsx (5 doctors with schedules)")
    print("- data/appointments.xlsx (empty, ready for bookings)")
