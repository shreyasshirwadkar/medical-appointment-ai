from typing import Dict, Any
from agents.greeting_agent import GreetingAgent
from agents.lookup_agent import LookupAgent
from agents.scheduling_agent import SchedulingAgent
from agents.insurance_agent import InsuranceAgent
from agents.reminder_agent import ReminderAgent
from utils.excel_export import ExcelExporter
from utils.email_service import EmailService

class SchedulingOrchestrator:
    """Main orchestrator that manages the flow between different agents."""
    
    def __init__(self):
        self.greeting_agent = GreetingAgent()
        self.lookup_agent = LookupAgent()
        self.scheduling_agent = SchedulingAgent()
        self.insurance_agent = InsuranceAgent()
        self.reminder_agent = ReminderAgent()
        self.excel_exporter = ExcelExporter()
        self.email_service = EmailService()
        
        # Track conversation state
        self.current_step = "greeting"
        self.collected_data = {
            "patient_info": {},
            "insurance_info": {},
            "appointment_info": {}
        }
    
    def process_message(self, user_input: str, patient_data: Dict[str, Any], appointment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process user message and route to appropriate agent."""
        
        # Initialize or update collected data
        if patient_data:
            self.collected_data["patient_info"].update(patient_data)
        if appointment_data:
            self.collected_data["appointment_info"].update(appointment_data)
        
        # Determine current step if not set
        if not hasattr(self, 'current_step'):
            self.current_step = self._determine_current_step()
        
        # Route to appropriate agent
        if self.current_step == "greeting":
            return self._handle_greeting(user_input)
        
        elif self.current_step == "lookup":
            return self._handle_lookup()
        
        elif self.current_step == "scheduling":
            return self._handle_scheduling(user_input)
        
        elif self.current_step == "insurance_collection":
            return self._handle_insurance(user_input)
        
        elif self.current_step == "confirmation":
            return self._handle_confirmation()
        
        else:
            return {
                "message": "I'm sorry, I'm not sure how to help with that. Let me start over. What's your name?",
                "patient_data": {},
                "appointment_data": {}
            }
    
    def _handle_greeting(self, user_input: str) -> Dict[str, Any]:
        """Handle patient greeting and information collection."""
        
        result = self.greeting_agent.process(user_input, self.collected_data["patient_info"])
        
        # Update collected data
        self.collected_data["patient_info"].update(result["extracted_data"])
        
        # Check if ready to move to next step
        if result["is_complete"]:
            self.current_step = "lookup"
            
            # Immediately process lookup
            lookup_result = self._handle_lookup()
            return {
                "message": result["message"] + "\\n\\n" + lookup_result["message"],
                "patient_data": self.collected_data["patient_info"],
                "appointment_data": self.collected_data["appointment_info"]
            }
        
        return {
            "message": result["message"],
            "patient_data": self.collected_data["patient_info"],
            "appointment_data": self.collected_data["appointment_info"]
        }
    
    def _handle_lookup(self) -> Dict[str, Any]:
        """Handle patient lookup in database."""
        
        result = self.lookup_agent.process(self.collected_data["patient_info"])
        
        # Update appointment data with lookup results
        self.collected_data["appointment_info"].update({
            "patient_type": result["patient_type"],
            "patient_id": result["patient_id"],
            "appointment_duration": result["appointment_duration"]
        })
        
        self.current_step = "scheduling"
        
        return {
            "message": result["message"],
            "patient_data": self.collected_data["patient_info"],
            "appointment_data": self.collected_data["appointment_info"]
        }
    
    def _handle_scheduling(self, user_input: str) -> Dict[str, Any]:
        """Handle appointment scheduling."""
        
        result = self.scheduling_agent.process(
            user_input, 
            self.collected_data["patient_info"],
            self.collected_data["appointment_info"]
        )
        
        # Update appointment data
        if "appointment_details" in result:
            self.collected_data["appointment_info"].update(result["appointment_details"])
        
        # Check if appointment was successfully booked
        if result.get("booking_successful"):
            self.current_step = "insurance_collection"
        
        return {
            "message": result["message"],
            "patient_data": self.collected_data["patient_info"],
            "appointment_data": self.collected_data["appointment_info"]
        }
    
    def _handle_insurance(self, user_input: str) -> Dict[str, Any]:
        """Handle insurance information collection."""
        
        result = self.insurance_agent.process(user_input, self.collected_data["insurance_info"])
        
        # Update insurance data
        self.collected_data["insurance_info"].update(result["extracted_insurance"])
        
        # Check if insurance collection is complete
        if result["is_complete"]:
            self.current_step = "confirmation"
            
            # Immediately process confirmation
            confirmation_result = self._handle_confirmation()
            return {
                "message": result["message"] + "\\n\\n" + confirmation_result["message"],
                "patient_data": self.collected_data["patient_info"],
                "appointment_data": self.collected_data["appointment_info"]
            }
        
        return {
            "message": result["message"],
            "patient_data": self.collected_data["patient_info"],
            "appointment_data": self.collected_data["appointment_info"]
        }
    
    def _handle_confirmation(self) -> Dict[str, Any]:
        """Handle final appointment confirmation and setup reminders."""
        
        # Generate Excel report
        excel_file = self.excel_exporter.export_appointment(
            patient_data=self.collected_data["patient_info"],
            appointment_data=self.collected_data["appointment_info"],
            insurance_data=self.collected_data["insurance_info"]
        )
        
        # Schedule reminders
        reminder_result = self.reminder_agent.schedule_reminders(
            self.collected_data["appointment_info"],
            self.collected_data["patient_info"]
        )
        
        # Send confirmation email with intake forms
        email_sent = self.email_service.send_confirmation_email(
            patient_data=self.collected_data["patient_info"],
            appointment_data=self.collected_data["appointment_info"],
            insurance_data=self.collected_data["insurance_info"]
        )
        
        appointment_date = self.collected_data["appointment_info"]["datetime"].strftime("%A, %B %d, %Y at %I:%M %p")
        
        confirmation_message = f"""
        🎉 Your appointment is fully confirmed!
        
        📧 Confirmation Details:
        • Confirmation email sent: {'✅' if email_sent else '❌'}
        • Excel report generated: {'✅' if excel_file else '❌'}
        • Reminders scheduled: {reminder_result.get('total_reminders', 0)} reminders
        
        📋 Next Steps:
        1. Check your email for intake forms
        2. Complete forms before your appointment
        3. Bring photo ID and insurance card
        4. Arrive 15 minutes early
        
        📞 Need to make changes?
        Contact us at least 24 hours in advance to reschedule or cancel.
        
        We look forward to seeing you on {appointment_date}!
        """
        
        # Reset for next patient
        self.current_step = "greeting"
        self.collected_data = {
            "patient_info": {},
            "insurance_info": {},
            "appointment_info": {}
        }
        
        return {
            "message": confirmation_message,
            "patient_data": {},
            "appointment_data": {},
            "booking_complete": True
        }
    
    def _determine_current_step(self) -> str:
        """Determine current step based on collected data."""
        
        patient_info = self.collected_data["patient_info"]
        appointment_info = self.collected_data["appointment_info"]
        insurance_info = self.collected_data["insurance_info"]
        
        # Check if basic patient info is complete
        required_patient_fields = ["name", "date_of_birth", "preferred_doctor", "location"]
        patient_complete = all(field in patient_info and patient_info[field] for field in required_patient_fields)
        
        if not patient_complete:
            return "greeting"
        
        # Check if lookup has been done
        if "patient_type" not in appointment_info:
            return "lookup"
        
        # Check if appointment is scheduled
        if "appointment_id" not in appointment_info:
            return "scheduling"
        
        # Check if insurance is collected
        required_insurance_fields = ["insurance_carrier", "member_id"]
        insurance_complete = all(field in insurance_info and insurance_info[field] for field in required_insurance_fields)
        
        if not insurance_complete:
            return "insurance_collection"
        
        return "confirmation"
