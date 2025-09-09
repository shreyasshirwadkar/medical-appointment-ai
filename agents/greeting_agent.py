from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Dict, Any
import re
from datetime import datetime
from config import DEMO_MODE

# Import mock LLM for demo mode
if DEMO_MODE:
    from utils.mock_llm import MockChatOpenAI

class GreetingAgent:
    """Agent responsible for greeting patients and collecting basic information."""
    
    def __init__(self, llm_model: str = "gpt-3.5-turbo"):
        if DEMO_MODE:
            self.llm = MockChatOpenAI(model=llm_model, temperature=0.1)
        else:
            self.llm = ChatOpenAI(model=llm_model, temperature=0.1)
        self.required_fields = ["name", "date_of_birth", "preferred_doctor", "location"]
        
    def process(self, user_input: str, collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process user input to extract patient information."""
        
        # Create system prompt
        system_prompt = f"""
        You are a friendly medical receptionist AI helping patients schedule appointments.
        Your job is to greet patients warmly and collect the following required information:
        - Full name
        - Date of birth (MM/DD/YYYY format)
        - Preferred doctor
        - Preferred location/clinic
        
        Current collected information: {collected_data}
        
        Be conversational, professional, and empathetic. If information is missing, ask for it politely.
        If all required information is collected, confirm the details and proceed to the next step.
        
        Extract any provided information and return it in a structured format.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_input)
        ]
        
        # Get LLM response
        response = self.llm(messages)
        ai_message = response.content
        
        # Extract structured data from the input
        extracted_data = self._extract_patient_info(user_input, collected_data)
        
        # Check completion status
        missing_fields = [field for field in self.required_fields if field not in extracted_data or not extracted_data[field]]
        is_complete = len(missing_fields) == 0
        
        return {
            "message": ai_message,
            "extracted_data": extracted_data,
            "is_complete": is_complete,
            "missing_fields": missing_fields,
            "next_step": "lookup" if is_complete else "continue_greeting"
        }
    
    def _extract_patient_info(self, text: str, existing_data: Dict) -> Dict[str, Any]:
        """Extract patient information from text using regex patterns."""
        data = existing_data.copy()
        
        # Extract name (look for patterns like "My name is John Doe" or "I'm Jane Smith")
        name_patterns = [
            r"(?:my name is|i'm|i am|name's)\s+([a-zA-Z\s]+)",
            r"^([A-Z][a-z]+\s+[A-Z][a-z]+)",  # First Last name pattern
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and not data.get("name"):
                data["name"] = match.group(1).strip().title()
                break
        
        # Extract date of birth (MM/DD/YYYY or MM-DD-YYYY)
        dob_pattern = r"(\d{1,2}[/-]\d{1,2}[/-]\d{4})"
        dob_match = re.search(dob_pattern, text)
        if dob_match and not data.get("date_of_birth"):
            data["date_of_birth"] = dob_match.group(1)
        
        # Extract doctor preference
        doctor_patterns = [
            r"(?:doctor|dr\.?)\s+([a-zA-Z\s]+)",
            r"(?:see|with|appointment with)\s+(?:doctor|dr\.?)\s+([a-zA-Z\s]+)",
        ]
        
        for pattern in doctor_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and not data.get("preferred_doctor"):
                data["preferred_doctor"] = match.group(1).strip().title()
                break
        
        # Extract location
        location_keywords = ["location", "clinic", "office", "branch"]
        for keyword in location_keywords:
            pattern = f"{keyword}[:\s]+([a-zA-Z\s]+)"
            match = re.search(pattern, text, re.IGNORECASE)
            if match and not data.get("location"):
                data["location"] = match.group(1).strip().title()
                break
        
        return data
