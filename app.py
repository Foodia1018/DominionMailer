import streamlit as st
import os
import pandas as pd
from database import DBManager
from utils import Helpers

# Set page configuration
st.set_page_config(
    page_title="DominionMailer",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables if they don't exist
if "db" not in st.session_state:
    st.session_state.db = DBManager("dominion_mailer_data.db")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = True  # Demo mode, always authenticated

# App title and description
st.title("📧 DominionMailer")
st.markdown("#### *Design like a creator. Deliver like a machine.*")

# Dashboard overview
st.header("Dashboard")

# Create a 3-column layout for key metrics
col1, col2, col3 = st.columns(3)

# Get data from database
campaigns = st.session_state.db.get_campaigns()
total_campaigns = len(campaigns) if campaigns else 0

recipient_lists = st.session_state.db.get_recipient_lists()
total_recipient_lists = len(recipient_lists) if recipient_lists else 0

total_recipients = st.session_state.db.get_total_recipients()

with col1:
    st.info(f"**Total Campaigns:** {total_campaigns}")
    
with col2:
    st.info(f"**Recipient Lists:** {total_recipient_lists}")
    
with col3:
    st.info(f"**Total Recipients:** {total_recipients}")

# Recent campaigns
st.subheader("Recent Campaigns")

if campaigns and len(campaigns) > 0:
    recent_campaigns_df = pd.DataFrame(campaigns)
    # Display only relevant columns
    if len(recent_campaigns_df) > 0:
        display_columns = ["name", "status", "updated_at"]
        display_columns = [col for col in display_columns if col in recent_campaigns_df.columns]
        st.dataframe(recent_campaigns_df[display_columns].head(5))
else:
    st.markdown("No campaigns yet. Create your first campaign from the **Campaigns** page.")

# Quick actions
st.subheader("Quick Actions")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("➕ New Campaign", use_container_width=True):
        st.switch_page("pages/1_Campaigns.py")

with col2:
    if st.button("👥 Manage Recipients", use_container_width=True):
        st.switch_page("pages/2_Recipients.py")

with col3:
    if st.button("📊 View Analytics", use_container_width=True):
        st.switch_page("pages/4_Analytics.py")

# Footer
st.markdown("---")
st.markdown("DominionMailer v0.1.0 - *© 2023 DominionMailer*")
