from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Dict, Any, List
from datetime import datetime, timedelta
import pandas as pd
from utils.calendar_integration import CalendarIntegration
from utils.database import Database
from config import DEMO_MODE

# Import mock LLM for demo mode
if DEMO_MODE:
    from utils.mock_llm import MockChatOpenAI

class SchedulingAgent:
    """Agent responsible for finding and booking appointment slots."""
    
    def __init__(self, llm_model: str = "gpt-3.5-turbo"):
        if DEMO_MODE:
            self.llm = MockChatOpenAI(model=llm_model, temperature=0.1)
        else:
            self.llm = ChatOpenAI(model=llm_model, temperature=0.1)
        self.calendar = CalendarIntegration()
        self.db = Database()
        
    def process(self, user_input: str, patient_data: Dict[str, Any], appointment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process scheduling requests and find available slots."""
        
        duration = appointment_data.get("appointment_duration", 60)
        preferred_doctor = patient_data.get("preferred_doctor")
        location = patient_data.get("location")
        
        # Get available slots
        available_slots = self.calendar.get_available_slots(
            doctor=preferred_doctor,
            location=location,
            duration=duration,
            days_ahead=14  # Look 2 weeks ahead
        )
        
        if not available_slots:
            return {
                "message": f"I'm sorry, but Dr. {preferred_doctor} doesn't have any available {duration}-minute slots " \
                          f"in the next two weeks at our {location} location. Would you like me to check with " \
                          f"another doctor or a different location?",
                "available_slots": [],
                "next_step": "alternative_options"
            }
        
        # Format available slots for presentation
        formatted_slots = self._format_slots_for_display(available_slots[:6])  # Show top 6 options
        
        system_prompt = f"""
        You are a medical receptionist AI helping a patient schedule an appointment.
        Present the available appointment slots in a friendly, organized manner.
        
        Patient: {patient_data.get('name')}
        Doctor: {preferred_doctor}
        Duration: {duration} minutes
        Location: {location}
        
        Be helpful and ask the patient to choose their preferred time.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Show available appointments: {formatted_slots}")
        ]
        
        response = self.llm(messages)
        
        # Check if user selected a time slot
        selected_slot = self._extract_selected_slot(user_input, available_slots)
        
        if selected_slot:
            return self._confirm_appointment(selected_slot, patient_data, appointment_data)
        
        return {
            "message": response.content + "\\n\\n" + formatted_slots,
            "available_slots": available_slots,
            "next_step": "slot_selection"
        }
    
    def _format_slots_for_display(self, slots: List[Dict]) -> str:
        """Format available slots for user-friendly display."""
        if not slots:
            return "No available slots found."
        
        formatted = "Here are the available appointment times:\\n\\n"
        for i, slot in enumerate(slots, 1):
            date_str = slot['datetime'].strftime("%A, %B %d, %Y")
            time_str = slot['datetime'].strftime("%I:%M %p")
            formatted += f"{i}. {date_str} at {time_str}\\n"
        
        formatted += "\\nPlease let me know which time works best for you by saying the number or date and time."
        return formatted
    
    def _extract_selected_slot(self, user_input: str, available_slots: List[Dict]) -> Dict:
        """Extract user's selected time slot from their input."""
        user_input_lower = user_input.lower()
        
        # Look for number selection (e.g., "1", "option 2", "number 3")
        import re
        number_match = re.search(r'(?:option\s+)?(?:number\s+)?(\d+)', user_input_lower)
        if number_match:
            try:
                slot_index = int(number_match.group(1)) - 1
                if 0 <= slot_index < len(available_slots):
                    return available_slots[slot_index]
            except ValueError:
                pass
        
        # Look for date/time mentions
        for slot in available_slots:
            date_str = slot['datetime'].strftime("%B %d").lower()
            time_str = slot['datetime'].strftime("%I:%M").lower().lstrip('0')
            
            if date_str in user_input_lower or time_str in user_input_lower:
                return slot
        
        return None
    
    def _confirm_appointment(self, selected_slot: Dict, patient_data: Dict, appointment_data: Dict) -> Dict:
        """Confirm the selected appointment slot."""
        
        appointment_details = {
            "appointment_id": self.db.generate_appointment_id(),
            "patient_id": appointment_data.get("patient_id"),
            "doctor": patient_data.get("preferred_doctor"),
            "datetime": selected_slot['datetime'],
            "duration": appointment_data.get("appointment_duration"),
            "location": patient_data.get("location"),
            "status": "confirmed",
            "created_at": datetime.now()
        }
        
        # Book the appointment
        success = self.calendar.book_appointment(selected_slot, appointment_details)
        
        if success:
            # Save to database
            self.db.save_appointment(appointment_details)
            
            date_str = selected_slot['datetime'].strftime("%A, %B %d, %Y")
            time_str = selected_slot['datetime'].strftime("%I:%M %p")
            
            message = f"Perfect! I've scheduled your appointment for {date_str} at {time_str} " \
                     f"with Dr. {patient_data.get('preferred_doctor')} at our {patient_data.get('location')} location. " \
                     f"Your appointment ID is {appointment_details['appointment_id']}. " \
                     f"Now let's collect your insurance information to complete the booking."
            
            return {
                "message": message,
                "appointment_details": appointment_details,
                "next_step": "insurance_collection",
                "booking_successful": True
            }
        else:
            return {
                "message": "I'm sorry, but that time slot is no longer available. Let me show you other options.",
                "booking_successful": False,
                "next_step": "reschedule"
            }
