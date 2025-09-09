from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Dict, Any, List
import pandas as pd
from utils.database import Database
from config import DEMO_MODE

# Import mock LLM for demo mode
if DEMO_MODE:
    from utils.mock_llm import MockChatOpenAI

class LookupAgent:
    """Agent responsible for looking up patients in the EMR system."""
    
    def __init__(self, llm_model: str = "gpt-3.5-turbo"):
        if DEMO_MODE:
            self.llm = MockChatOpenAI(model=llm_model, temperature=0.1)
        else:
            self.llm = ChatOpenAI(model=llm_model, temperature=0.1)
        self.db = Database()
        
    def process(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Look up patient in the database and determine if new or returning."""
        
        # Search for existing patient
        search_results = self.db.search_patient(
            name=patient_data.get("name"),
            dob=patient_data.get("date_of_birth")
        )
        
        if search_results:
            # Returning patient
            patient_record = search_results[0]  # Take first match
            
            system_prompt = """
            You are a medical receptionist AI. A returning patient has been found in the system.
            Greet them warmly, acknowledge their return, and ask if they want to schedule 
            with their usual doctor or if there are any changes to their information.
            
            Be professional and make them feel welcome back.
            """
            
            message = f"Welcome back, {patient_data['name']}! I found your record in our system. " \
                     f"I see you've been a patient since {patient_record.get('first_visit', 'your last visit')}. " \
                     f"Would you like to schedule with Dr. {patient_record.get('usual_doctor', patient_data.get('preferred_doctor'))} " \
                     f"as usual, or would you prefer a different doctor today?"
            
            return {
                "message": message,
                "patient_type": "returning",
                "patient_id": patient_record.get("patient_id"),
                "patient_record": patient_record,
                "appointment_duration": 30,  # 30 minutes for returning patients
                "next_step": "scheduling"
            }
        else:
            # New patient
            system_prompt = """
            You are a medical receptionist AI. This is a new patient who hasn't been to our clinic before.
            Welcome them warmly, explain that they're a new patient which means they'll need a longer 
            appointment for a comprehensive evaluation, and let them know about the intake forms they'll need to complete.
            
            Be welcoming and helpful in explaining the process.
            """
            
            message = f"Welcome to our clinic, {patient_data['name']}! I don't see you in our system yet, " \
                     f"so you'll be scheduled as a new patient. This means we'll reserve 60 minutes for your " \
                     f"appointment to allow time for a comprehensive evaluation. You'll also receive intake " \
                     f"forms to complete before your visit. Let's find you an available appointment time."
            
            # Create new patient record
            new_patient_id = self.db.create_patient_record(patient_data)
            
            return {
                "message": message,
                "patient_type": "new",
                "patient_id": new_patient_id,
                "patient_record": patient_data,
                "appointment_duration": 60,  # 60 minutes for new patients
                "next_step": "scheduling"
            }
    
    def get_patient_history(self, patient_id: str) -> List[Dict]:
        """Retrieve patient's appointment history."""
        return self.db.get_patient_appointments(patient_id)
