import pandas as pd
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
import os

class Database:
    """Mock database class for managing patient and appointment data."""
    
    def __init__(self):
        self.patients_file = "data/patients.csv"
        self.appointments_file = "data/appointments.xlsx"
        self.reminders_file = "data/reminders.csv"
        
        # Initialize data files if they don't exist
        self._initialize_data_files()
    
    def _initialize_data_files(self):
        """Initialize data files with headers if they don't exist."""
        
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        # Initialize patients file
        if not os.path.exists(self.patients_file):
            patients_df = pd.DataFrame(columns=[
                'patient_id', 'name', 'date_of_birth', 'email', 'phone',
                'preferred_doctor', 'location', 'first_visit', 'usual_doctor',
                'insurance_carrier', 'member_id', 'group_number'
            ])
            patients_df.to_csv(self.patients_file, index=False)
        
        # Initialize appointments file
        if not os.path.exists(self.appointments_file):
            appointments_df = pd.DataFrame(columns=[
                'appointment_id', 'patient_id', 'doctor', 'datetime',
                'duration', 'location', 'status', 'created_at'
            ])
            appointments_df.to_excel(self.appointments_file, index=False)
        
        # Initialize reminders file
        if not os.path.exists(self.reminders_file):
            reminders_df = pd.DataFrame(columns=[
                'reminder_id', 'appointment_id', 'patient_id', 'reminder_datetime',
                'days_before', 'type', 'status', 'response'
            ])
            reminders_df.to_csv(self.reminders_file, index=False)
    
    def search_patient(self, name: str, dob: str) -> List[Dict]:
        """Search for a patient by name and date of birth."""
        
        try:
            patients_df = pd.read_csv(self.patients_file)
            
            # Search by name (case insensitive)
            name_match = patients_df[patients_df['name'].str.lower() == name.lower()]
            
            if not name_match.empty:
                # Further filter by DOB if provided
                if dob:
                    dob_match = name_match[name_match['date_of_birth'] == dob]
                    if not dob_match.empty:
                        return dob_match.to_dict('records')
                
                return name_match.to_dict('records')
            
            return []
        
        except Exception as e:
            print(f"Error searching patient: {e}")
            return []
    
    def create_patient_record(self, patient_data: Dict[str, Any]) -> str:
        """Create a new patient record."""
        
        patient_id = str(uuid.uuid4())[:8]
        
        new_record = {
            'patient_id': patient_id,
            'name': patient_data.get('name', ''),
            'date_of_birth': patient_data.get('date_of_birth', ''),
            'email': patient_data.get('email', ''),
            'phone': patient_data.get('phone', ''),
            'preferred_doctor': patient_data.get('preferred_doctor', ''),
            'location': patient_data.get('location', ''),
            'first_visit': datetime.now().strftime('%Y-%m-%d'),
            'usual_doctor': patient_data.get('preferred_doctor', ''),
            'insurance_carrier': '',
            'member_id': '',
            'group_number': ''
        }
        
        try:
            patients_df = pd.read_csv(self.patients_file)
            patients_df = pd.concat([patients_df, pd.DataFrame([new_record])], ignore_index=True)
            patients_df.to_csv(self.patients_file, index=False)
            
            return patient_id
        
        except Exception as e:
            print(f"Error creating patient record: {e}")
            return None
    
    def save_appointment(self, appointment_data: Dict[str, Any]) -> bool:
        """Save appointment to database."""
        
        try:
            appointments_df = pd.read_excel(self.appointments_file)
            
            new_appointment = {
                'appointment_id': appointment_data['appointment_id'],
                'patient_id': appointment_data['patient_id'],
                'doctor': appointment_data['doctor'],
                'datetime': appointment_data['datetime'].isoformat(),
                'duration': appointment_data['duration'],
                'location': appointment_data['location'],
                'status': appointment_data['status'],
                'created_at': appointment_data['created_at'].isoformat()
            }
            
            appointments_df = pd.concat([appointments_df, pd.DataFrame([new_appointment])], ignore_index=True)
            appointments_df.to_excel(self.appointments_file, index=False)
            
            return True
        
        except Exception as e:
            print(f"Error saving appointment: {e}")
            return False
    
    def get_appointment(self, appointment_id: str) -> Dict:
        """Get appointment by ID."""
        
        try:
            appointments_df = pd.read_excel(self.appointments_file)
            appointment = appointments_df[appointments_df['appointment_id'] == appointment_id]
            
            if not appointment.empty:
                record = appointment.iloc[0].to_dict()
                # Convert datetime string back to datetime object
                record['datetime'] = datetime.fromisoformat(record['datetime'])
                record['created_at'] = datetime.fromisoformat(record['created_at'])
                return record
            
            return {}
        
        except Exception as e:
            print(f"Error getting appointment: {e}")
            return {}
    
    def get_patient(self, patient_id: str) -> Dict:
        """Get patient by ID."""
        
        try:
            patients_df = pd.read_csv(self.patients_file)
            patient = patients_df[patients_df['patient_id'] == patient_id]
            
            if not patient.empty:
                return patient.iloc[0].to_dict()
            
            return {}
        
        except Exception as e:
            print(f"Error getting patient: {e}")
            return {}
    
    def get_patient_appointments(self, patient_id: str) -> List[Dict]:
        """Get all appointments for a patient."""
        
        try:
            appointments_df = pd.read_excel(self.appointments_file)
            patient_appointments = appointments_df[appointments_df['patient_id'] == patient_id]
            
            appointments = []
            for _, row in patient_appointments.iterrows():
                appointment = row.to_dict()
                appointment['datetime'] = datetime.fromisoformat(appointment['datetime'])
                appointment['created_at'] = datetime.fromisoformat(appointment['created_at'])
                appointments.append(appointment)
            
            return appointments
        
        except Exception as e:
            print(f"Error getting patient appointments: {e}")
            return []
    
    def save_reminder(self, reminder_data: Dict[str, Any]) -> bool:
        """Save reminder to database."""
        
        try:
            reminders_df = pd.read_csv(self.reminders_file)
            
            new_reminder = {
                'reminder_id': reminder_data['reminder_id'],
                'appointment_id': reminder_data['appointment_id'],
                'patient_id': reminder_data['patient_id'],
                'reminder_datetime': reminder_data['reminder_datetime'].isoformat(),
                'days_before': reminder_data['days_before'],
                'type': reminder_data['type'],
                'status': reminder_data['status'],
                'response': ''
            }
            
            reminders_df = pd.concat([reminders_df, pd.DataFrame([new_reminder])], ignore_index=True)
            reminders_df.to_csv(self.reminders_file, index=False)
            
            return True
        
        except Exception as e:
            print(f"Error saving reminder: {e}")
            return False
    
    def update_reminder_status(self, reminder_id: str, status: str) -> bool:
        """Update reminder status."""
        
        try:
            reminders_df = pd.read_csv(self.reminders_file)
            reminders_df.loc[reminders_df['reminder_id'] == reminder_id, 'status'] = status
            reminders_df.to_csv(self.reminders_file, index=False)
            return True
        
        except Exception as e:
            print(f"Error updating reminder status: {e}")
            return False
    
    def update_reminder_response(self, reminder_id: str, status: str, response: str) -> bool:
        """Update reminder response."""
        
        try:
            reminders_df = pd.read_csv(self.reminders_file)
            reminders_df.loc[reminders_df['reminder_id'] == reminder_id, 'status'] = status
            reminders_df.loc[reminders_df['reminder_id'] == reminder_id, 'response'] = response
            reminders_df.to_csv(self.reminders_file, index=False)
            return True
        
        except Exception as e:
            print(f"Error updating reminder response: {e}")
            return False
    
    def generate_appointment_id(self) -> str:
        """Generate a unique appointment ID."""
        return f"APT{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:6].upper()}"
