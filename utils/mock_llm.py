"""
Mock LLM implementation for demo purposes when OpenAI API is not available.
"""

from typing import List, Dict, Any
import random

class MockMessage:
    """Mock message response."""
    def __init__(self, content: str):
        self.content = content

class MockChatGeneration:
    """Mock chat generation."""
    def __init__(self, message: MockMessage):
        self.message = message

class MockGenerationResult:
    """Mock generation result."""
    def __init__(self, generations: List[List[MockChatGeneration]]):
        self.generations = generations

class MockChatOpenAI:
    """Mock implementation of ChatOpenAI for demo purposes."""
    
    def __init__(self, model: str = "mock", temperature: float = 0.1, **kwargs):
        self.model = model
        self.temperature = temperature
        
    def __call__(self, messages) -> MockMessage:
        """Mock the LLM call with predefined responses."""
        return self._generate_mock_response(messages)
    
    def generate(self, messages, **kwargs) -> MockGenerationResult:
        """Mock the generate method."""
        generations = []
        for message_list in messages:
            response = self._generate_mock_response(message_list)
            generations.append([MockChatGeneration(message=response)])
        return MockGenerationResult(generations=generations)
    
    def _generate_mock_response(self, messages) -> MockMessage:
        """Generate appropriate mock responses based on the context."""
        
        # Try to extract human message content
        last_message = ""
        if hasattr(messages, '__iter__'):
            for msg in messages:
                if hasattr(msg, 'content'):
                    last_message = msg.content.lower()
                elif isinstance(msg, str):
                    last_message = msg.lower()
        elif hasattr(messages, 'content'):
            last_message = messages.content.lower()
        elif isinstance(messages, str):
            last_message = messages.lower()
        
        # Enhanced mock responses for different contexts
        if any(word in last_message for word in ['hello', 'hi', 'start', 'schedule', 'appointment']):
            responses = [
                "Hello! I'd be happy to help you schedule an appointment. Could you please provide your full name and date of birth?",
                "Welcome! To get started, I'll need your name and date of birth to look up your information.",
                "Hi there! Let's schedule your appointment. What's your full name and date of birth?"
            ]
        elif any(name in last_message for name in ['shreya', 'john', 'jane', 'smith']) and ('1999' in last_message or 'birth' in last_message or '/' in last_message):
            responses = [
                "Thank you, Shreya! I found your information in our system. You're a returning patient. What type of appointment would you like to schedule today?",
                "Perfect! I have your details in our records. What brings you in for this appointment?",
                "Great! I see you in our system. What kind of medical service do you need?"
            ]
        elif any(word in last_message for word in ['physiotherapy', 'physical therapy', 'pt', 'muscle', 'tear', 'injury', 'pain', 'leg']):
            responses = [
                "I understand you need a physiotherapy appointment for your leg muscle tear. Let me check our availability. What's your preferred date and time?",
                "A physiotherapy appointment for leg muscle tear - I can help with that! Do you have any preferred days this week?",
                "Got it! Physiotherapy for leg muscle treatment. Would you prefer a morning or afternoon appointment?"
            ]
        elif any(word in last_message for word in ['tomorrow', 'today', 'sept', 'september', '3', 'monday', 'tuesday', 'wednesday']):
            responses = [
                "Perfect! I can schedule you for tomorrow, September 3rd. We have slots available at 9:00 AM, 11:00 AM, 2:00 PM, or 4:00 PM. Which time works best for you?",
                "Great choice! For September 3rd, I have availability at 10:00 AM, 1:00 PM, or 3:30 PM. What time would you prefer?",
                "Excellent! Tomorrow (Sept 3rd) works well. Would you prefer a morning appointment (9:30 AM, 11:00 AM) or afternoon (2:00 PM, 4:00 PM)?"
            ]
        elif any(time in last_message for time in ['9', '10', '11', '1', '2', '3', '4', 'am', 'pm', 'morning', 'afternoon']):
            responses = [
                "Perfect! I've tentatively booked you for September 3rd at that time. Now I'll need your insurance information to complete the booking. What's your insurance provider?",
                "Great choice! Before I confirm your appointment, I need to collect your insurance details. What insurance company do you have?",
                "Excellent! That time slot is yours. To finalize the booking, please provide your insurance carrier name and member ID."
            ]
        elif any(word in last_message for word in ['insurance', 'coverage', 'blue cross', 'aetna', 'cigna', 'humana', 'medicare']):
            responses = [
                "Thank you! I'll need your member ID number as well to verify coverage. What's your member ID?",
                "Great! And what's your member ID or policy number for insurance verification?",
                "Perfect! Could you also provide your insurance member ID to complete the verification?"
            ]
        elif any(pattern in last_message for pattern in ['id', 'member', 'policy', '123', '456', '789']) or len([x for x in last_message.split() if x.isdigit() and len(x) > 5]):
            responses = [
                "Excellent! Your appointment is now confirmed for September 3rd. You'll receive a confirmation email shortly with intake forms to complete before your visit.",
                "Perfect! Your physiotherapy appointment is booked and confirmed. I'll send you the appointment details and intake forms via email.",
                "Great! Everything is set up. Your appointment confirmation and pre-visit forms will be emailed to you within the next few minutes."
            ]
        elif any(word in last_message for word in ['confirm', 'yes', 'correct', 'right', 'ok', 'okay']):
            responses = [
                "Wonderful! Your appointment has been successfully scheduled. You should receive an email confirmation with all the details and any required forms.",
                "Perfect! Your booking is complete. Check your email for the confirmation and please arrive 15 minutes early for check-in.",
                "Excellent! All set. Your appointment details and intake forms have been sent to your email address."
            ]
        elif any(word in last_message for word in ['no', 'cancel', 'change', 'reschedule']):
            responses = [
                "No problem! Would you like to look at different appointment times, or is there something else I can help you with?",
                "That's okay! Let me know if you'd like to explore other options or if you need assistance with anything else.",
                "Sure! Would you prefer a different time slot, or would you like to schedule for a different day?"
            ]
        elif any(word in last_message for word in ['thanks', 'thank you', 'bye', 'goodbye', 'done']):
            responses = [
                "You're welcome! Your appointment is all set. Don't forget to complete the intake forms before your visit. Have a great day!",
                "My pleasure! Everything is confirmed. Please remember to bring your insurance card and arrive 15 minutes early. Take care!",
                "Happy to help! Your physiotherapy appointment is scheduled and confirmed. See you soon!"
            ]
        else:
            responses = [
                "I'd be happy to help! Could you please provide more specific information about what you need assistance with?",
                "I want to make sure I understand correctly. Could you rephrase that or provide more details?",
                "Let me help you with that. Could you be more specific about what you're looking for?"
            ]
        
        return MockMessage(content=random.choice(responses))
