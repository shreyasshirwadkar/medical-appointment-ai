from twilio.rest import Client
from typing import Dict, Any
import config

class SMSService:
    """SMS service for sending appointment reminders via Twilio."""
    
    def __init__(self):
        self.account_sid = config.TWILIO_ACCOUNT_SID
        self.auth_token = config.TWILIO_AUTH_TOKEN
        self.from_number = "+1234567890"  # Replace with your Twilio number
        
        # Initialize Twilio client if credentials are available
        if self.account_sid and self.auth_token:
            try:
                self.client = Client(self.account_sid, self.auth_token)
            except Exception as e:
                print(f"Error initializing Twilio client: {e}")
                self.client = None
        else:
            self.client = None
    
    def send_reminder_sms(self, to_phone: str, message: str) -> bool:
        """Send SMS reminder to patient."""
        
        try:
            # Clean phone number format
            clean_phone = self._clean_phone_number(to_phone)
            
            if not clean_phone:
                print("Invalid phone number format")
                return False
            
            if self.client:
                # Send actual SMS
                message_obj = self.client.messages.create(
                    body=message,
                    from_=self.from_number,
                    to=clean_phone
                )
                
                print(f"SMS sent successfully. SID: {message_obj.sid}")
                return True
            else:
                # Simulate SMS sending for demo
                print(f"SMS would be sent to: {clean_phone}")
                print(f"Message: {message}")
                return True
                
        except Exception as e:
            print(f"Error sending SMS: {e}")
            return False
    
    def send_appointment_confirmation_sms(self, patient_phone: str, patient_name: str, appointment_data: Dict[str, Any]) -> bool:
        """Send appointment confirmation SMS."""
        
        appointment_date = appointment_data['datetime'].strftime('%m/%d/%Y')
        appointment_time = appointment_data['datetime'].strftime('%I:%M %p')
        doctor_name = appointment_data.get('doctor', 'your doctor')
        
        message = f"""
Hi {patient_name}! Your appointment is confirmed:

📅 {appointment_date} at {appointment_time}
👨‍⚕️ Dr. {doctor_name}
📍 {appointment_data.get('location', 'Our clinic')}

Please arrive 15 minutes early. Bring ID & insurance card. 

Confirmation ID: {appointment_data.get('appointment_id', '')}
        """.strip()
        
        return self.send_reminder_sms(patient_phone, message)
    
    def send_form_reminder_sms(self, patient_phone: str, patient_name: str, appointment_date: str) -> bool:
        """Send intake form completion reminder SMS."""
        
        message = f"""
Hi {patient_name}! Friendly reminder to complete your intake forms before your appointment on {appointment_date}. 

If you need help or haven't received them, please call us. Thanks!
        """.strip()
        
        return self.send_reminder_sms(patient_phone, message)
    
    def send_confirmation_request_sms(self, patient_phone: str, patient_name: str, appointment_data: Dict[str, Any]) -> bool:
        """Send appointment confirmation request SMS."""
        
        appointment_date = appointment_data['datetime'].strftime('%m/%d/%Y')
        appointment_time = appointment_data['datetime'].strftime('%I:%M %p')
        
        message = f"""
Hi {patient_name}! Your appointment with Dr. {appointment_data.get('doctor', 'your doctor')} is tomorrow ({appointment_date} at {appointment_time}).

Please reply:
✅ YES to confirm
❌ NO to cancel
🔄 RESCHEDULE if you need to change

Thank you!
        """.strip()
        
        return self.send_reminder_sms(patient_phone, message)
    
    def _clean_phone_number(self, phone: str) -> str:
        """Clean and format phone number for SMS."""
        
        if not phone:
            return ""
        
        # Remove all non-digit characters
        digits_only = ''.join(filter(str.isdigit, phone))
        
        # Add country code if missing
        if len(digits_only) == 10:
            return f"+1{digits_only}"
        elif len(digits_only) == 11 and digits_only.startswith('1'):
            return f"+{digits_only}"
        elif len(digits_only) > 11:
            return f"+{digits_only}"
        else:
            return ""
    
    def process_sms_response(self, from_phone: str, message: str) -> Dict[str, Any]:
        """Process incoming SMS responses from patients."""
        
        message_lower = message.lower().strip()
        
        # Determine response type
        if any(word in message_lower for word in ['yes', 'confirm', 'confirmed', 'y']):
            response_type = 'confirmed'
            status_message = "Appointment confirmed via SMS"
        
        elif any(word in message_lower for word in ['no', 'cancel', 'n']):
            response_type = 'cancelled'
            status_message = "Appointment cancelled via SMS"
        
        elif any(word in message_lower for word in ['reschedule', 'change', 'move']):
            response_type = 'reschedule_requested'
            status_message = "Reschedule requested via SMS"
        
        elif any(word in message_lower for word in ['completed', 'done', 'filled']):
            response_type = 'forms_completed'
            status_message = "Intake forms completed via SMS"
        
        else:
            response_type = 'other'
            status_message = "Response received via SMS"
        
        return {
            'from_phone': from_phone,
            'message': message,
            'response_type': response_type,
            'status_message': status_message,
            'requires_followup': response_type in ['cancelled', 'reschedule_requested']
        }
    
    def send_bulk_reminders(self, reminder_list: list) -> Dict[str, Any]:
        """Send bulk SMS reminders."""
        
        results = {
            'total_sent': 0,
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        for reminder in reminder_list:
            try:
                success = self.send_reminder_sms(
                    reminder['phone'], 
                    reminder['message']
                )
                
                results['total_sent'] += 1
                
                if success:
                    results['successful'] += 1
                else:
                    results['failed'] += 1
                    
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Failed to send to {reminder.get('phone', 'unknown')}: {str(e)}")
        
        return results
