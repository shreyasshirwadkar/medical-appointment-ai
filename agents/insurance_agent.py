from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Dict, Any
from config import DEMO_MODE

# Import mock LLM for demo mode
if DEMO_MODE:
    from utils.mock_llm import MockChatOpenAI
import re

class InsuranceAgent:
    """Agent responsible for collecting patient insurance information."""
    
    def __init__(self, llm_model: str = "gpt-3.5-turbo"):
        if DEMO_MODE:
            self.llm = MockChatOpenAI(model=llm_model, temperature=0.1)
        else:
            self.llm = ChatOpenAI(model=llm_model, temperature=0.1)
        self.required_fields = ["insurance_carrier", "member_id", "group_number"]
        
    def process(self, user_input: str, collected_insurance: Dict[str, Any]) -> Dict[str, Any]:
        """Process user input to extract insurance information."""
        
        system_prompt = f"""
        You are a medical receptionist AI collecting insurance information from a patient.
        You need to collect:
        - Insurance carrier/company name
        - Member ID number
        - Group number (if applicable)
        
        Current collected information: {collected_insurance}
        
        Be professional and explain why this information is needed.
        Ask for missing information politely and provide guidance on where to find it 
        (insurance card, employer benefits, etc.).
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_input)
        ]
        
        response = self.llm(messages)
        ai_message = response.content
        
        # Extract insurance information from user input
        extracted_insurance = self._extract_insurance_info(user_input, collected_insurance)
        
        # Check completion status
        missing_fields = [field for field in self.required_fields if field not in extracted_insurance or not extracted_insurance[field]]
        is_complete = len(missing_fields) == 0
        
        if is_complete:
            confirmation_message = f"""
            Thank you! I have your insurance information:
            
            • Insurance Carrier: {extracted_insurance['insurance_carrier']}
            • Member ID: {extracted_insurance['member_id']}
            • Group Number: {extracted_insurance.get('group_number', 'Not provided')}
            
            Your appointment is now fully booked! You'll receive a confirmation email shortly 
            with your appointment details and intake forms to complete before your visit.
            """
            
            return {
                "message": confirmation_message,
                "extracted_insurance": extracted_insurance,
                "is_complete": True,
                "next_step": "confirmation"
            }
        
        return {
            "message": ai_message,
            "extracted_insurance": extracted_insurance,
            "is_complete": False,
            "missing_fields": missing_fields,
            "next_step": "continue_insurance"
        }
    
    def _extract_insurance_info(self, text: str, existing_data: Dict) -> Dict[str, Any]:
        """Extract insurance information from text using regex patterns."""
        data = existing_data.copy()
        
        # Common insurance carriers
        carriers = [
            "aetna", "anthem", "blue cross", "blue shield", "cigna", "humana", 
            "kaiser", "united healthcare", "uhc", "medicare", "medicaid"
        ]
        
        text_lower = text.lower()
        
        # Extract insurance carrier
        if not data.get("insurance_carrier"):
            for carrier in carriers:
                if carrier in text_lower:
                    data["insurance_carrier"] = carrier.title()
                    break
            
            # Look for other carrier patterns
            carrier_patterns = [
                r"(?:insurance|carrier|company)\s+(?:is\s+)?([a-zA-Z\s&]+)",
                r"i have\s+([a-zA-Z\s&]+)\s+insurance",
            ]
            
            for pattern in carrier_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match and not data.get("insurance_carrier"):
                    carrier = match.group(1).strip()
                    if len(carrier) > 2:  # Avoid capturing single words
                        data["insurance_carrier"] = carrier.title()
                        break
        
        # Extract member ID (numbers, letters, or combination)
        member_id_patterns = [
            r"(?:member\s+id|member\s+number|id\s+number|policy\s+number)[:\s]+([a-zA-Z0-9]+)",
            r"(?:id|number)[:\s]+([a-zA-Z0-9]{6,})",  # At least 6 characters
        ]
        
        for pattern in member_id_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and not data.get("member_id"):
                data["member_id"] = match.group(1)
                break
        
        # Extract group number
        group_patterns = [
            r"(?:group\s+number|group\s+id)[:\s]+([a-zA-Z0-9]+)",
            r"group[:\s]+([a-zA-Z0-9]+)",
        ]
        
        for pattern in group_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and not data.get("group_number"):
                data["group_number"] = match.group(1)
                break
        
        return data
    
    def validate_insurance_info(self, insurance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate insurance information format."""
        validation_results = {
            "is_valid": True,
            "errors": []
        }
        
        # Validate member ID format (basic validation)
        member_id = insurance_data.get("member_id", "")
        if len(member_id) < 6:
            validation_results["errors"].append("Member ID seems too short. Please double-check.")
            validation_results["is_valid"] = False
        
        # Check for required carrier
        if not insurance_data.get("insurance_carrier"):
            validation_results["errors"].append("Insurance carrier is required.")
            validation_results["is_valid"] = False
        
        return validation_results
