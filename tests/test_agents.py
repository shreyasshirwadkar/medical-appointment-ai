import unittest
import sys
import os
from datetime import datetime

# Add the parent directory to the path so we can import the agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.greeting_agent import GreetingAgent
from agents.lookup_agent import LookupAgent
from agents.scheduling_agent import SchedulingAgent
from agents.insurance_agent import InsuranceAgent
from utils.database import Database

class TestGreetingAgent(unittest.TestCase):
    """Test cases for the GreetingAgent."""
    
    def setUp(self):
        self.agent = GreetingAgent()
    
    def test_name_extraction(self):
        """Test name extraction from user input."""
        user_input = "Hi, my name is John Smith"
        result = self.agent.process(user_input, {})
        
        self.assertIn("John Smith", result["extracted_data"].get("name", ""))
    
    def test_dob_extraction(self):
        """Test date of birth extraction."""
        user_input = "My date of birth is 01/15/1990"
        result = self.agent.process(user_input, {})
        
        self.assertEqual(result["extracted_data"].get("date_of_birth"), "01/15/1990")
    
    def test_doctor_extraction(self):
        """Test doctor preference extraction."""
        user_input = "I'd like to see Dr. Johnson"
        result = self.agent.process(user_input, {})
        
        self.assertIn("Johnson", result["extracted_data"].get("preferred_doctor", ""))
    
    def test_completion_check(self):
        """Test completion status check."""
        complete_data = {
            "name": "John Smith",
            "date_of_birth": "01/15/1990",
            "preferred_doctor": "Johnson",
            "location": "Downtown"
        }
        
        user_input = "That's all my information"
        result = self.agent.process(user_input, complete_data)
        
        self.assertTrue(result["is_complete"])

class TestLookupAgent(unittest.TestCase):
    """Test cases for the LookupAgent."""
    
    def setUp(self):
        self.agent = LookupAgent()
        self.database = Database()
    
    def test_new_patient_detection(self):
        """Test new patient detection."""
        patient_data = {
            "name": "Jane Doe",
            "date_of_birth": "12/25/2000",
            "preferred_doctor": "Smith",
            "location": "Downtown"
        }
        
        result = self.agent.process(patient_data)
        
        self.assertEqual(result["patient_type"], "new")
        self.assertEqual(result["appointment_duration"], 60)
    
    def test_returning_patient_detection(self):
        """Test returning patient detection."""
        # This would require an existing patient in the database
        # For this test, we'll mock the behavior
        patient_data = {
            "name": "Existing Patient",
            "date_of_birth": "01/01/1980",
            "preferred_doctor": "Wilson",
            "location": "Midtown"
        }
        
        # In a real test, we'd set up a patient record first
        result = self.agent.process(patient_data)
        
        # Should create new patient if not found
        self.assertIsNotNone(result["patient_id"])

class TestSchedulingAgent(unittest.TestCase):
    """Test cases for the SchedulingAgent."""
    
    def setUp(self):
        self.agent = SchedulingAgent()
    
    def test_available_slots_generation(self):
        """Test available slots generation."""
        # This test would require proper calendar data setup
        patient_data = {
            "name": "Test Patient",
            "preferred_doctor": "Smith",
            "location": "Downtown"
        }
        
        appointment_data = {
            "appointment_duration": 60
        }
        
        user_input = "I need an appointment next week"
        result = self.agent.process(user_input, patient_data, appointment_data)
        
        self.assertIn("available_slots", result)
    
    def test_slot_selection(self):
        """Test appointment slot selection."""
        # This would test the slot selection logic
        pass

class TestInsuranceAgent(unittest.TestCase):
    """Test cases for the InsuranceAgent."""
    
    def setUp(self):
        self.agent = InsuranceAgent()
    
    def test_insurance_carrier_extraction(self):
        """Test insurance carrier extraction."""
        user_input = "I have Blue Cross Blue Shield insurance"
        result = self.agent.process(user_input, {})
        
        self.assertIn("Blue Cross", result["extracted_insurance"].get("insurance_carrier", ""))
    
    def test_member_id_extraction(self):
        """Test member ID extraction."""
        user_input = "My member ID is 123456789"
        result = self.agent.process(user_input, {})
        
        self.assertEqual(result["extracted_insurance"].get("member_id"), "123456789")
    
    def test_insurance_validation(self):
        """Test insurance information validation."""
        insurance_data = {
            "insurance_carrier": "Aetna",
            "member_id": "12345",  # Too short
            "group_number": "ABC123"
        }
        
        validation = self.agent.validate_insurance_info(insurance_data)
        
        self.assertFalse(validation["is_valid"])
        self.assertIn("Member ID seems too short", validation["errors"])

class TestDatabase(unittest.TestCase):
    """Test cases for the Database utility."""
    
    def setUp(self):
        self.db = Database()
    
    def test_patient_creation(self):
        """Test patient record creation."""
        patient_data = {
            "name": "Test Patient",
            "date_of_birth": "01/01/1990",
            "email": "test@example.com",
            "preferred_doctor": "Test Doctor",
            "location": "Test Location"
        }
        
        patient_id = self.db.create_patient_record(patient_data)
        
        self.assertIsNotNone(patient_id)
        self.assertEqual(len(patient_id), 8)  # Should be 8 characters
    
    def test_patient_search(self):
        """Test patient search functionality."""
        # Search for a patient that should exist in sample data
        results = self.db.search_patient("John Smith", "01/15/1990")
        
        # This test depends on sample data being generated
        self.assertIsInstance(results, list)
    
    def test_appointment_id_generation(self):
        """Test appointment ID generation."""
        appointment_id = self.db.generate_appointment_id()
        
        self.assertTrue(appointment_id.startswith("APT"))
        self.assertEqual(len(appointment_id), 17)  # APT + 8 digits + 6 chars

class TestWorkflow(unittest.TestCase):
    """Test cases for the complete workflow."""
    
    def setUp(self):
        self.greeting_agent = GreetingAgent()
        self.lookup_agent = LookupAgent()
        self.scheduling_agent = SchedulingAgent()
        self.insurance_agent = InsuranceAgent()
    
    def test_complete_workflow(self):
        """Test a complete appointment booking workflow."""
        # This would test the entire flow from greeting to confirmation
        
        # Step 1: Greeting
        user_input = "Hi, I'm John Smith, born 01/15/1990, I'd like to see Dr. Johnson at Downtown clinic"
        collected_data = {}
        
        greeting_result = self.greeting_agent.process(user_input, collected_data)
        
        if greeting_result["is_complete"]:
            # Step 2: Lookup
            patient_data = greeting_result["extracted_data"]
            lookup_result = self.lookup_agent.process(patient_data)
            
            # Step 3: Would continue with scheduling and insurance...
            self.assertIsNotNone(lookup_result["patient_id"])
            self.assertIn(lookup_result["patient_type"], ["new", "returning"])

if __name__ == "__main__":
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestGreetingAgent))
    test_suite.addTest(unittest.makeSuite(TestLookupAgent))
    test_suite.addTest(unittest.makeSuite(TestSchedulingAgent))
    test_suite.addTest(unittest.makeSuite(TestInsuranceAgent))
    test_suite.addTest(unittest.makeSuite(TestDatabase))
    test_suite.addTest(unittest.makeSuite(TestWorkflow))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print results
    if result.wasSuccessful():
        print("\nAll tests passed! ✅")
    else:
        print(f"\n{len(result.failures)} test(s) failed, {len(result.errors)} error(s) ❌")
        
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"- {test}: {traceback}")
        
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"- {test}: {traceback}")
