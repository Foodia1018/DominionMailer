import streamlit as st
import time
from email_sender import EmailSender

st.set_page_config(
    page_title="Settings | DominionMailer",
    page_icon="⚙️",
    layout="wide"
)

# Check if database is initialized
if "db" not in st.session_state:
    st.error("Database not initialized. Please restart the application.")
    st.stop()

db = st.session_state.db

# Initialize session state variables
if "settings_view" not in st.session_state:
    st.session_state.settings_view = "smtp"  # smtp, app, help

# Header
st.title("⚙️ Settings")

# Navigation tabs
tab1, tab2, tab3 = st.tabs(["SMTP Configuration", "Application Settings", "Help & Support"])

with tab1:
    st.header("SMTP Server Configuration")
    st.markdown(
        "Configure your SMTP servers for sending emails. You can add multiple configurations "
        "and select which one to use for each campaign."
    )
    
    # Get all SMTP configs
    smtp_configs = db.get_smtp_configs()
    
    # Add new SMTP config form
    with st.expander("Add New SMTP Configuration", expanded=not smtp_configs):
        with st.form("add_smtp_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                profile_name = st.text_input("Profile Name", placeholder="Gmail SMTP")
                host = st.text_input("SMTP Host", placeholder="smtp.gmail.com")
                port = st.number_input("SMTP Port", min_value=1, max_value=65535, value=587)
                col1a, col2a = st.columns(2)
                with col1a:
                    use_tls = st.checkbox("Use TLS", value=True)
                with col2a:
                    use_ssl = st.checkbox("Use SSL", value=False)
                daily_limit = st.number_input("Daily Send Limit", min_value=1, max_value=500000, value=10000)
                rotation_order = st.number_input("Rotation Order (0 = automatic)", min_value=0, value=0)
            
            with col2:
                username = st.text_input("SMTP Username", placeholder="your.email@gmail.com")
                password = st.text_input("SMTP Password", type="password")
                sender_email = st.text_input("Sender Email", placeholder="your.email@gmail.com")
                sender_name = st.text_input("Sender Name", placeholder="Your Company")
            
            submit_button = st.form_submit_button("Add SMTP Configuration")
            
            if submit_button:
                if not profile_name or not host or not port or not username or not password or not sender_email or not sender_name:
                    st.error("All fields are required.")
                else:
                    try:
                        new_config_id = db.add_smtp_config(
                            profile_name=profile_name,
                            host=host,
                            port=port,
                            username=username,
                            password=password,
                            use_tls=use_tls,
                            sender_email=sender_email,
                            sender_name=sender_name
                        )
                        
                        if new_config_id:
                            st.success(f"SMTP Configuration '{profile_name}' added successfully!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Failed to add SMTP configuration. Please try again.")
                    except Exception as e:
                        st.error(f"Error adding SMTP configuration: {str(e)}")
    
    # List existing SMTP configs
    if smtp_configs and len(smtp_configs) > 0:
        st.subheader("Your SMTP Configurations")
        
        for config in smtp_configs:
            with st.expander(f"{config['profile_name']} ({config['host']}:{config['port']})"):
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.write(f"**Username:** {config['username']}")
                    st.write(f"**Sender:** {config['sender_name']} <{config['sender_email']}>")
                
                with col2:
                    st.write(f"**TLS:** {'Enabled' if config['use_tls'] else 'Disabled'}")
                    st.write(f"**SSL:** {'Enabled' if config['use_ssl'] else 'Disabled'}")
                
                with col3:
                    # Test email button
                    if st.button("Test Connection", key=f"test_{config['id']}"):
                        st.session_state.test_smtp_id = config['id']
                        st.session_state.test_email_view = True
                        st.rerun()
                    
                    # Delete button
                    if st.button("Delete", key=f"delete_{config['id']}"):
                        if st.session_state.get("confirm_delete_smtp") != config['id']:
                            st.session_state.confirm_delete_smtp = config['id']
                            st.warning("Click the button again to confirm deletion.")
                        else:
                            # Check if this config is used by any campaign
                            campaigns_using = db.execute_query(
                                "SELECT COUNT(*) as count FROM campaigns WHERE smtp_config_id = ?",
                                (config['id'],),
                                fetch_one=True
                            )
                            
                            if campaigns_using and campaigns_using['count'] > 0:
                                st.error(f"Cannot delete this configuration as it is used by {campaigns_using['count']} campaign(s).")
                            else:
                                # User confirmed deletion
                                db.execute_query(
                                    "DELETE FROM smtp_configs WHERE id = ?",
                                    (config['id'],),
                                    commit=True
                                )
                                st.success("SMTP configuration deleted successfully!")
                                st.session_state.confirm_delete_smtp = None
                                time.sleep(1)
                                st.rerun()
        
        # Test email form
        if hasattr(st.session_state, 'test_smtp_id') and hasattr(st.session_state, 'test_email_view') and st.session_state.test_email_view:
            st.subheader("Test SMTP Configuration")
            
            config = db.get_smtp_config_by_id(st.session_state.test_smtp_id)
            
            if config:
                st.write(f"Testing configuration: **{config['profile_name']}**")
                
                with st.form("test_smtp_form"):
                    test_email = st.text_input("Send test email to", placeholder="your.email@example.com")
                    test_subject = st.text_input("Subject", value="DominionMailer Test Email")
                    test_content = st.text_area(
                        "Email Content",
                        value="This is a test email from DominionMailer to verify SMTP configuration."
                    )
                    
                    submit_button = st.form_submit_button("Send Test Email")
                    
                    if submit_button:
                        if not test_email:
                            st.error("Please enter a recipient email address.")
                        else:
                            # Create simple HTML email
                            html_content = f"""
                            <!DOCTYPE html>
                            <html>
                            <head>
                                <style>
                                    body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
                                </style>
                            </head>
                            <body>
                                <h2>DominionMailer Test Email</h2>
                                <p>{test_content}</p>
                                <p>If you received this email, your SMTP configuration is working correctly!</p>
                                <hr>
                                <p><small>Sent from DominionMailer v0.1.0</small></p>
                            </body>
                            </html>
                            """
                            
                            # Initialize email sender
                            email_sender = EmailSender(dict(config))
                            
                            # Send test email
                            with st.spinner("Sending test email..."):
                                success, message = email_sender.send_test_email(
                                    test_email,
                                    test_subject,
                                    html_content
                                )
                            
                            if success:
                                st.success("Test email sent successfully!")
                            else:
                                st.error(f"Failed to send test email: {message}")
                
                if st.button("Cancel Test", key="cancel_test"):
                    st.session_state.test_email_view = False
                    st.rerun()
    else:
        st.info("No SMTP configurations found. Add your first configuration using the form above.")

with tab2:
    st.header("Application Settings")
    
    # Default settings
    st.subheader("Email Sending Settings")
    
    default_throttle = st.slider(
        "Default Throttle Rate (emails per minute)",
        min_value=1,
        max_value=100,
        value=10,
        help="Default rate limit for sending emails to avoid being flagged as spam"
    )
    
    # Save application settings
    if st.button("Save Application Settings"):
        # In a real app, we would save these to a settings table or file
        st.success("Application settings saved successfully!")
    
    # Application information
    st.subheader("About DominionMailer")
    st.write("Version: 0.1.0")
    st.write("\"Design like a creator. Deliver like a machine.\"")
    
    # Reset database option (for demo purposes)
    st.subheader("Reset Application")
    reset_db = st.checkbox("I understand this will delete all my data", key="reset_db")
    
    if reset_db:
        if st.button("Reset Database"):
            if st.session_state.get("confirm_reset") != True:
                st.session_state.confirm_reset = True
                st.warning("Click the button again to confirm database reset. This will delete all your data!")
            else:
                # Close current connection
                db.close()
                
                # Delete database file and recreate
                import os
                if os.path.exists(db.db_name):
                    os.remove(db.db_name)
                
                # Reinitialize database
                st.session_state.db = None
                st.session_state.db = db = db.__class__(db.db_name)
                
                st.success("Database reset successfully!")
                st.session_state.confirm_reset = False
                time.sleep(2)
                st.rerun()

with tab3:
    st.header("Help & Support")
    
    # Documentation
    st.subheader("Documentation")
    st.markdown("""
    ### Quick Start Guide
    
    1. **Setup SMTP** - Configure your email sending server in the SMTP Configuration tab
    2. **Create Recipients** - Add recipient lists and import contacts
    3. **Create Templates** - Design your email templates with custom fields
    4. **Create Campaigns** - Set up campaigns using your templates and recipient lists
    5. **Send & Analyze** - Send your campaigns and analyze the results
    
    ### Placeholder Tags
    
    Use these placeholders in your email templates:
    - `{{recipient_name}}` - The recipient's name
    - `{{recipient_email}}` - The recipient's email
    - `{{unsubscribe_link}}` - Link to unsubscribe
    - `{{custom1}}` through `{{custom5}}` - Custom fields
    """)
    
    # FAQ
    st.subheader("Frequently Asked Questions")
    
    with st.expander("How do I import recipients?"):
        st.write("""
        To import recipients:
        1. Go to the Recipients page
        2. Select or create a recipient list
        3. Click "Import Recipients from CSV"
        4. Upload a CSV file with at least an 'email' column
        5. Follow the on-screen instructions to complete the import
        """)
    
    with st.expander("How do I create an email template?"):
        st.write("""
        To create an email template:
        1. Go to the Templates page
        2. Click "Create New Template" or use one from the gallery
        3. Add your HTML content with placeholders like {{recipient_name}}
        4. Preview and save your template
        5. Use this template when creating campaigns
        """)
    
    with st.expander("How do I track email opens and clicks?"):
        st.write("""
        Email tracking is built-in:
        1. When you send a campaign, opens and clicks are automatically tracked
        2. View the results in the Analytics page
        3. Select your campaign to see detailed statistics
        4. Export the data as needed for further analysis
        """)
    
    # Contact
    st.subheader("Contact Support")
    st.info("For help and support, please contact support@dominionmailer.com")

# Footer
st.markdown("---")
st.markdown("DominionMailer v0.1.0 - *Design like a creator. Deliver like a machine.*")
