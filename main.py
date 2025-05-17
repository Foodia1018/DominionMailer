
import streamlit as st
import os
import sys
from database import DBManager
from utils import Helpers

def init_app():
    """Initialize the application"""
    # Set page configuration
    st.set_page_config(
        page_title="DominionMailer",
        page_icon="📧",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize database if not exists
    if "db" not in st.session_state:
        st.session_state.db = DBManager("dominion_mailer_data.db")
        
    # Initialize authentication state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = True

def main():
    init_app()
    # Import and run the main app
    import app
    
if __name__ == "__main__":
    main()
