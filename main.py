import streamlit as st
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.orchestrator import SchedulingOrchestrator
from utils.database import Database
import config

def main():
    st.set_page_config(
        page_title=config.APP_TITLE,
        page_icon="🏥",
        layout="wide"
    )
    
    st.title("🏥 AI Medical Scheduling Agent")
    st.markdown(config.APP_DESCRIPTION)
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.orchestrator = SchedulingOrchestrator()
        st.session_state.patient_data = {}
        st.session_state.appointment_data = {}
    
    # Sidebar with patient info
    with st.sidebar:
        st.header("📋 Current Session")
        if st.session_state.patient_data:
            st.json(st.session_state.patient_data)
        
        if st.session_state.appointment_data:
            st.header("📅 Appointment Details")
            st.json(st.session_state.appointment_data)
        
        if st.button("🔄 Reset Session"):
            st.session_state.messages = []
            st.session_state.patient_data = {}
            st.session_state.appointment_data = {}
            st.rerun()
    
    # Chat interface
    chat_container = st.container()
    
    with chat_container:
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("How can I help you schedule your appointment today?"):
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Process with orchestrator
            with st.chat_message("assistant"):
                with st.spinner("Processing..."):
                    response = st.session_state.orchestrator.process_message(
                        prompt, 
                        st.session_state.patient_data,
                        st.session_state.appointment_data
                    )
                    
                    st.markdown(response["message"])
                    
                    # Update session data
                    if "patient_data" in response:
                        st.session_state.patient_data.update(response["patient_data"])
                    
                    if "appointment_data" in response:
                        st.session_state.appointment_data.update(response["appointment_data"])
                    
                    # Add assistant message to chat
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response["message"]
                    })
            
            st.rerun()

if __name__ == "__main__":
    main()
