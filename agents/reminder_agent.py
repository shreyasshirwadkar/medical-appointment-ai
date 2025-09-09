from typing import Dict, Any, List
from datetime import datetime, timedelta
import schedule
from utils.email_service import EmailService
from utils.sms_service import SMSService
from utils.database import Database

class ReminderAgent:
    """Agent responsible for scheduling and sending appointment reminders."""
    
    def __init__(self):
        self.email_service = EmailService()
        self.sms_service = SMSService()
        self.db = Database()
        self.reminder_schedule = [7, 3, 1]  # Days before appointment
        
    def schedule_reminders(self, appointment_data: Dict[str, Any], patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule all reminders for an appointment."""
        
        appointment_datetime = appointment_data['datetime']
        appointment_id = appointment_data['appointment_id']
        
        scheduled_reminders = []
        
        for days_before in self.reminder_schedule:
            reminder_datetime = appointment_datetime - timedelta(days=days_before)
            
            # Only schedule if reminder time is in the future
            if reminder_datetime > datetime.now():
                reminder_data = {
                    "reminder_id": f"{appointment_id}_{days_before}d",
                    "appointment_id": appointment_id,
                    "patient_id": patient_data.get("patient_id"),
                    "reminder_datetime": reminder_datetime,
                    "days_before": days_before,
                    "type": self._get_reminder_type(days_before),
                    "status": "scheduled"
                }
                
                # Save reminder to database
                self.db.save_reminder(reminder_data)
                scheduled_reminders.append(reminder_data)
        
        return {
            "scheduled_reminders": scheduled_reminders,
            "total_reminders": len(scheduled_reminders)
        }
    
    def send_reminder(self, reminder_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send a specific reminder to the patient."""
        
        # Get appointment and patient details
        appointment = self.db.get_appointment(reminder_data['appointment_id'])
        patient = self.db.get_patient(reminder_data['patient_id'])
        
        if not appointment or not patient:
            return {"success": False, "error": "Appointment or patient not found"}
        
        reminder_type = reminder_data.get('type', 'standard')
        
        # Generate reminder message based on type
        message = self._generate_reminder_message(reminder_type, appointment, patient)
        
        # Send email reminder
        email_sent = self.email_service.send_reminder_email(
            to_email=patient.get('email'),
            subject=f"Appointment Reminder - {appointment['datetime'].strftime('%m/%d/%Y')}",
            message=message,
            appointment_data=appointment
        )
        
        # Send SMS reminder
        sms_sent = self.sms_service.send_reminder_sms(
            to_phone=patient.get('phone'),
            message=self._generate_sms_message(reminder_type, appointment)
        )
        
        # Update reminder status
        self.db.update_reminder_status(reminder_data['reminder_id'], 'sent')
        
        return {
            "success": True,
            "email_sent": email_sent,
            "sms_sent": sms_sent,
            "reminder_type": reminder_type
        }
    
    def _get_reminder_type(self, days_before: int) -> str:
        """Determine reminder type based on days before appointment."""
        if days_before == 7:
            return "initial"
        elif days_before == 3:
            return "form_check"
        elif days_before == 1:
            return "confirmation"
        else:
            return "standard"
    
    def _generate_reminder_message(self, reminder_type: str, appointment: Dict, patient: Dict) -> str:
        """Generate reminder message based on type."""
        
        patient_name = patient.get('name', 'Patient')
        doctor_name = appointment.get('doctor', 'your doctor')
        appointment_date = appointment['datetime'].strftime('%A, %B %d, %Y')
        appointment_time = appointment['datetime'].strftime('%I:%M %p')
        location = appointment.get('location', 'our clinic')
        
        base_message = f"""
        Dear {patient_name},
        
        This is a reminder about your upcoming appointment:
        
        📅 Date: {appointment_date}
        🕐 Time: {appointment_time}
        👨‍⚕️ Doctor: Dr. {doctor_name}
        📍 Location: {location}
        
        """
        
        if reminder_type == "initial":
            return base_message + """
            Your appointment is scheduled for one week from now. Please make sure to:
            
            ✅ Mark your calendar
            ✅ Arrange transportation if needed
            ✅ Prepare any questions you'd like to ask
            
            You'll receive additional reminders with more details closer to your appointment date.
            
            If you need to reschedule, please call us at least 24 hours in advance.
            
            Best regards,
            The Medical Scheduling Team
            """
        
        elif reminder_type == "form_check":
            return base_message + """
            Your appointment is in 3 days! 
            
            📋 IMPORTANT: Have you completed your intake forms yet?
            
            If you haven't received them or need assistance, please let us know immediately.
            Completing these forms in advance helps ensure your appointment runs smoothly.
            
            Please confirm that you've received and completed your forms by replying to this email.
            
            If you need to cancel or reschedule, please do so at least 24 hours in advance.
            
            Best regards,
            The Medical Scheduling Team
            """
        
        elif reminder_type == "confirmation":
            return base_message + """
            Your appointment is TOMORROW! 
            
            🔍 Final Checklist:
            ✅ Intake forms completed?
            ✅ Insurance card ready?
            ✅ Photo ID available?
            ✅ List of current medications?
            
            ⚠️ PLEASE CONFIRM: Will you be able to keep this appointment?
            
            If you cannot attend, please contact us immediately as this affects other patients' scheduling.
            
            If you're experiencing any symptoms of illness, please call us to discuss whether 
            to proceed with your appointment or reschedule.
            
            We look forward to seeing you tomorrow!
            
            Best regards,
            The Medical Scheduling Team
            """
        
        else:
            return base_message + """
            Please don't forget about your upcoming appointment.
            
            If you have any questions or need to make changes, please contact us.
            
            Best regards,
            The Medical Scheduling Team
            """
    
    def _generate_sms_message(self, reminder_type: str, appointment: Dict) -> str:
        """Generate shorter SMS reminder message."""
        
        date = appointment['datetime'].strftime('%m/%d/%Y')
        time = appointment['datetime'].strftime('%I:%M%p')
        doctor = appointment.get('doctor', 'your doctor')
        
        if reminder_type == "initial":
            return f"Reminder: Appointment with Dr. {doctor} on {date} at {time}. More details to follow."
        
        elif reminder_type == "form_check":
            return f"Appointment in 3 days ({date} at {time}). Have you completed your intake forms? Reply if you need help."
        
        elif reminder_type == "confirmation":
            return f"Appointment TOMORROW {date} at {time} with Dr. {doctor}. Please confirm you can attend. Bring ID & insurance card."
        
        else:
            return f"Appointment reminder: {date} at {time} with Dr. {doctor}."
    
    def process_reminder_response(self, reminder_id: str, response: str) -> Dict[str, Any]:
        """Process patient response to reminder."""
        
        response_lower = response.lower().strip()
        
        # Analyze response
        if any(word in response_lower for word in ['yes', 'confirm', 'confirmed', 'will be there', 'attending']):
            status = 'confirmed'
            message = "Thank you for confirming your appointment!"
        
        elif any(word in response_lower for word in ['no', 'cancel', "can't", 'cannot', 'reschedule']):
            status = 'cancelled'
            message = "We've noted your cancellation. Please call us to reschedule when convenient."
        
        elif any(word in response_lower for word in ['completed', 'filled', 'done', 'finished']):
            status = 'forms_completed'
            message = "Great! Thank you for completing your forms."
        
        else:
            status = 'responded'
            message = "Thank you for your response. If you need assistance, please call us."
        
        # Update reminder status
        self.db.update_reminder_response(reminder_id, status, response)
        
        return {
            "status": status,
            "message": message,
            "requires_followup": status in ['cancelled', 'needs_help']
        }
