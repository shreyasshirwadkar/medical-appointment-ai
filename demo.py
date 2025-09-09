#!/usr/bin/env python3
"""
Demo script for AI Medical Scheduling Agent
Demonstrates the complete appointment booking workflow
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.orchestrator import SchedulingOrchestrator
from utils.database import Database
from datetime import datetime

def demo_conversation():
    """Demonstrate a complete conversation workflow."""
    
    print("🏥 AI Medical Scheduling Agent - Demo")
    print("=" * 50)
    print()
    
    # Initialize the orchestrator
    orchestrator = SchedulingOrchestrator()
    
    # Demo conversation steps
    demo_steps = [
        {
            "user": "Hi, I need to schedule an appointment",
            "description": "Initial greeting"
        },
        {
            "user": "My name is John Smith, date of birth 01/15/1990, I'd like to see Dr. Johnson at Downtown clinic",
            "description": "Providing patient information"
        },
        {
            "user": "I'd prefer next Tuesday around 2 PM if possible",
            "description": "Scheduling preference"
        },
        {
            "user": "Option 2 looks good",
            "description": "Selecting time slot"
        },
        {
            "user": "I have Blue Cross Blue Shield insurance, member ID 123456789, group number ABC123",
            "description": "Insurance information"
        }
    ]
    
    # Simulate conversation
    patient_data = {}
    appointment_data = {}
    
    for i, step in enumerate(demo_steps, 1):
        print(f"📝 Step {i}: {step['description']}")
        print(f"👤 User: {step['user']}")
        print()
        
        try:
            # Process the message
            response = orchestrator.process_message(
                step["user"], 
                patient_data, 
                appointment_data
            )
            
            # Update data
            if "patient_data" in response:
                patient_data.update(response["patient_data"])
            if "appointment_data" in response:
                appointment_data.update(response["appointment_data"])
            
            # Display AI response
            print(f"🤖 AI: {response['message']}")
            print()
            
            # Show collected data
            if patient_data:
                print("📊 Collected Patient Data:")
                for key, value in patient_data.items():
                    if value:
                        print(f"   • {key}: {value}")
                print()
            
            if appointment_data and any(appointment_data.values()):
                print("📅 Appointment Data:")
                for key, value in appointment_data.items():
                    if value:
                        if isinstance(value, datetime):
                            print(f"   • {key}: {value.strftime('%Y-%m-%d %H:%M')}")
                        else:
                            print(f"   • {key}: {value}")
                print()
            
            print("-" * 50)
            print()
            
        except Exception as e:
            print(f"❌ Error in step {i}: {str(e)}")
            print("This is expected in demo mode without full API setup")
            print()
    
    print("✅ Demo completed!")
    print()
    print("🎯 Key Features Demonstrated:")
    print("   • Natural language processing")
    print("   • Patient information extraction")
    print("   • Database lookup simulation")
    print("   • Appointment scheduling workflow")
    print("   • Insurance information collection")
    print("   • Multi-agent orchestration")
    print()

def show_sample_data():
    """Show sample data that would be generated."""
    
    print("📊 Sample Data Overview")
    print("=" * 30)
    print()
    
    # Try to show actual data if available
    try:
        db = Database()
        
        # Show patient count
        import pandas as pd
        patients_df = pd.read_csv("data/patients.csv")
        print(f"👥 Total Patients: {len(patients_df)}")
        print(f"📍 Locations: {', '.join(patients_df['location'].unique())}")
        print(f"👨‍⚕️ Doctors: {', '.join(patients_df['preferred_doctor'].unique())}")
        print()
        
        # Show sample patient
        sample_patient = patients_df.iloc[0]
        print("📋 Sample Patient Record:")
        print(f"   • Name: {sample_patient['name']}")
        print(f"   • DOB: {sample_patient['date_of_birth']}")
        print(f"   • Doctor: {sample_patient['preferred_doctor']}")
        print(f"   • Location: {sample_patient['location']}")
        print(f"   • Insurance: {sample_patient['insurance_carrier']}")
        print()
        
    except Exception as e:
        print("⚠️  Sample data not generated yet. Run 'python generate_sample_data.py' first.")
        print()

def show_architecture():
    """Show system architecture overview."""
    
    print("🏗️  System Architecture")
    print("=" * 25)
    print()
    print("┌─────────────────────────────────────┐")
    print("│           Streamlit UI              │")
    print("└─────────────────┬───────────────────┘")
    print("                  │")
    print("┌─────────────────┴───────────────────┐")
    print("│         Orchestrator Agent         │")
    print("└─────────────────┬───────────────────┘")
    print("                  │")
    print("      ┌───────────┼───────────┐")
    print("      │           │           │")
    print("┌─────┴─────┐ ┌───┴────┐ ┌───┴─────┐")
    print("│ Greeting  │ │Schedule│ │Insurance│")
    print("│  Agent    │ │ Agent  │ │  Agent  │")
    print("└───────────┘ └────────┘ └─────────┘")
    print("      │           │           │")
    print("┌─────┴─────┐ ┌───┴────┐ ┌───┴─────┐")
    print("│  Lookup   │ │Reminder│ │  Utils  │")
    print("│  Agent    │ │ Agent  │ │Services │")
    print("└───────────┘ └────────┘ └─────────┘")
    print()
    
    print("🔧 Core Components:")
    print("   • GreetingAgent: Collects patient info")
    print("   • LookupAgent: Searches patient database")
    print("   • SchedulingAgent: Manages appointments")
    print("   • InsuranceAgent: Handles insurance data")
    print("   • ReminderAgent: Sends automated reminders")
    print("   • Utility Services: Email, SMS, Excel export")
    print()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Medical Scheduling Agent Demo')
    parser.add_argument('--conversation', action='store_true', help='Run conversation demo')
    parser.add_argument('--data', action='store_true', help='Show sample data')
    parser.add_argument('--architecture', action='store_true', help='Show system architecture')
    parser.add_argument('--all', action='store_true', help='Run all demos')
    
    args = parser.parse_args()
    
    if args.all or (not any([args.conversation, args.data, args.architecture])):
        # Run all demos if no specific option is chosen
        show_architecture()
        show_sample_data()
        demo_conversation()
    else:
        if args.architecture:
            show_architecture()
        if args.data:
            show_sample_data()
        if args.conversation:
            demo_conversation()
