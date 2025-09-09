import requests
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime, timedelta
import json

class CalendarIntegration:
    """Integration with calendar systems (Calendly simulation)."""
    
    def __init__(self):
        self.doctors_schedule_file = "data/doctors_schedule.xlsx"
        self._initialize_doctors_schedule()
    
    def _initialize_doctors_schedule(self):
        """Initialize doctors schedule if not exists."""
        
        import os
        os.makedirs("data", exist_ok=True)
        
        if not os.path.exists(self.doctors_schedule_file):
            # Create sample doctor schedules
            doctors = [
                {"doctor": "Smith", "location": "Downtown", "weekday": "Monday", "start_time": "09:00", "end_time": "17:00"},
                {"doctor": "Smith", "location": "Downtown", "weekday": "Tuesday", "start_time": "09:00", "end_time": "17:00"},
                {"doctor": "Smith", "location": "Downtown", "weekday": "Wednesday", "start_time": "09:00", "end_time": "17:00"},
                {"doctor": "Smith", "location": "Downtown", "weekday": "Thursday", "start_time": "09:00", "end_time": "17:00"},
                {"doctor": "Smith", "location": "Downtown", "weekday": "Friday", "start_time": "09:00", "end_time": "15:00"},
                
                {"doctor": "Johnson", "location": "Uptown", "weekday": "Monday", "start_time": "08:00", "end_time": "16:00"},
                {"doctor": "Johnson", "location": "Uptown", "weekday": "Tuesday", "start_time": "08:00", "end_time": "16:00"},
                {"doctor": "Johnson", "location": "Uptown", "weekday": "Wednesday", "start_time": "08:00", "end_time": "16:00"},
                {"doctor": "Johnson", "location": "Uptown", "weekday": "Thursday", "start_time": "08:00", "end_time": "16:00"},
                {"doctor": "Johnson", "location": "Uptown", "weekday": "Friday", "start_time": "08:00", "end_time": "14:00"},
                
                {"doctor": "Wilson", "location": "Midtown", "weekday": "Monday", "start_time": "10:00", "end_time": "18:00"},
                {"doctor": "Wilson", "location": "Midtown", "weekday": "Tuesday", "start_time": "10:00", "end_time": "18:00"},
                {"doctor": "Wilson", "location": "Midtown", "weekday": "Wednesday", "start_time": "10:00", "end_time": "18:00"},
                {"doctor": "Wilson", "location": "Midtown", "weekday": "Thursday", "start_time": "10:00", "end_time": "18:00"},
                {"doctor": "Wilson", "location": "Midtown", "weekday": "Friday", "start_time": "10:00", "end_time": "16:00"},
            ]
            
            schedule_df = pd.DataFrame(doctors)
            schedule_df.to_excel(self.doctors_schedule_file, index=False)
    
    def get_available_slots(self, doctor: str, location: str, duration: int, days_ahead: int = 14) -> List[Dict]:
        """Get available appointment slots for a doctor."""
        
        try:
            schedule_df = pd.read_excel(self.doctors_schedule_file)
            
            # Filter by doctor and location
            doctor_schedule = schedule_df[
                (schedule_df['doctor'].str.lower() == doctor.lower()) &
                (schedule_df['location'].str.lower() == location.lower())
            ]
            
            if doctor_schedule.empty:
                return []
            
            available_slots = []
            current_date = datetime.now().date()
            
            # Generate slots for the next 'days_ahead' days
            for day_offset in range(1, days_ahead + 1):
                target_date = current_date + timedelta(days=day_offset)
                weekday_name = target_date.strftime('%A')
                
                # Find doctor's schedule for this weekday
                day_schedule = doctor_schedule[doctor_schedule['weekday'] == weekday_name]
                
                if not day_schedule.empty:
                    schedule_row = day_schedule.iloc[0]
                    start_time = datetime.strptime(schedule_row['start_time'], '%H:%M').time()
                    end_time = datetime.strptime(schedule_row['end_time'], '%H:%M').time()
                    
                    # Generate time slots
                    current_time = datetime.combine(target_date, start_time)
                    end_datetime = datetime.combine(target_date, end_time)
                    
                    while current_time + timedelta(minutes=duration) <= end_datetime:
                        # Check if slot is available (not booked)
                        if self._is_slot_available(doctor, location, current_time, duration):
                            available_slots.append({
                                'datetime': current_time,
                                'doctor': doctor,
                                'location': location,
                                'duration': duration,
                                'available': True
                            })
                        
                        # Move to next slot (30-minute intervals)
                        current_time += timedelta(minutes=30)
            
            return available_slots[:20]  # Limit to 20 slots
        
        except Exception as e:
            print(f"Error getting available slots: {e}")
            return []
    
    def _is_slot_available(self, doctor: str, location: str, datetime_slot: datetime, duration: int) -> bool:
        """Check if a specific time slot is available."""
        
        try:
            # Load existing appointments
            appointments_df = pd.read_excel("data/appointments.xlsx")
            
            if appointments_df.empty:
                return True
            
            # Convert datetime strings back to datetime objects for comparison
            appointments_df['datetime'] = pd.to_datetime(appointments_df['datetime'])
            
            # Check for conflicts
            slot_end = datetime_slot + timedelta(minutes=duration)
            
            conflicts = appointments_df[
                (appointments_df['doctor'].str.lower() == doctor.lower()) &
                (appointments_df['location'].str.lower() == location.lower()) &
                (appointments_df['status'] == 'confirmed') &
                (
                    # Overlap conditions
                    (appointments_df['datetime'] < slot_end) &
                    (appointments_df['datetime'] + pd.to_timedelta(appointments_df['duration'], unit='m') > datetime_slot)
                )
            ]
            
            return conflicts.empty
        
        except Exception as e:
            print(f"Error checking slot availability: {e}")
            return True  # Assume available if error
    
    def book_appointment(self, selected_slot: Dict, appointment_details: Dict) -> bool:
        """Book an appointment slot."""
        
        try:
            # In a real system, this would make an API call to Calendly
            # For simulation, we'll just mark the slot as booked
            
            # The appointment will be saved to the database by the calling function
            # Here we simulate a successful booking
            return True
        
        except Exception as e:
            print(f"Error booking appointment: {e}")
            return False
    
    def get_doctor_availability(self, doctor: str) -> Dict[str, Any]:
        """Get overall availability for a doctor."""
        
        try:
            schedule_df = pd.read_excel(self.doctors_schedule_file)
            doctor_schedule = schedule_df[schedule_df['doctor'].str.lower() == doctor.lower()]
            
            if doctor_schedule.empty:
                return {"available": False, "message": f"Dr. {doctor} not found in our system."}
            
            # Calculate total weekly hours
            total_hours = 0
            locations = set()
            weekdays = []
            
            for _, row in doctor_schedule.iterrows():
                start = datetime.strptime(row['start_time'], '%H:%M')
                end = datetime.strptime(row['end_time'], '%H:%M')
                hours = (end - start).total_seconds() / 3600
                total_hours += hours
                locations.add(row['location'])
                weekdays.append(row['weekday'])
            
            return {
                "available": True,
                "doctor": doctor,
                "total_weekly_hours": total_hours,
                "locations": list(locations),
                "weekdays": weekdays,
                "message": f"Dr. {doctor} is available {total_hours} hours per week across {len(locations)} location(s)."
            }
        
        except Exception as e:
            print(f"Error getting doctor availability: {e}")
            return {"available": False, "message": "Error checking availability."}
    
    def cancel_appointment(self, appointment_id: str) -> bool:
        """Cancel an appointment."""
        
        try:
            appointments_df = pd.read_excel("data/appointments.xlsx")
            appointments_df.loc[appointments_df['appointment_id'] == appointment_id, 'status'] = 'cancelled'
            appointments_df.to_excel("data/appointments.xlsx", index=False)
            return True
        
        except Exception as e:
            print(f"Error cancelling appointment: {e}")
            return False
    
    def reschedule_appointment(self, appointment_id: str, new_datetime: datetime) -> bool:
        """Reschedule an existing appointment."""
        
        try:
            appointments_df = pd.read_excel("data/appointments.xlsx")
            
            # Find the appointment
            appointment_idx = appointments_df[appointments_df['appointment_id'] == appointment_id].index
            
            if len(appointment_idx) == 0:
                return False
            
            # Update the datetime
            appointments_df.loc[appointment_idx[0], 'datetime'] = new_datetime.isoformat()
            appointments_df.to_excel("data/appointments.xlsx", index=False)
            
            return True
        
        except Exception as e:
            print(f"Error rescheduling appointment: {e}")
            return False
