import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
from email_sender import EmailSender
from utils import Helpers

st.set_page_config(
    page_title="Campaigns | DominionMailer",
    page_icon="📧",
    layout="wide"
)

# Check if database is initialized
if "db" not in st.session_state:
    st.error("Database not initialized. Please restart the application.")
    st.stop()

db = st.session_state.db

# Initialize session state variables
if "campaign_id" not in st.session_state:
    st.session_state.campaign_id = None

if "campaign_view" not in st.session_state:
    st.session_state.campaign_view = "list"  # list, create, edit, send

def reset_campaign_view():
    st.session_state.campaign_view = "list"
    st.session_state.campaign_id = None

# Header
st.title("📧 Campaign Management")

# Main campaign management interface
if st.session_state.campaign_view == "list":
    # Show campaign list with options to create new or edit existing
    st.subheader("Your Campaigns")
    
    # Create new campaign button
    if st.button("➕ Create New Campaign", key="new_campaign"):
        st.session_state.campaign_view = "create"
        st.rerun()
    
    # Get all campaigns
    campaigns = db.get_campaigns()
    
    if campaigns and len(campaigns) > 0:
        # Convert to DataFrame for display
        campaigns_df = pd.DataFrame([dict(c) for c in campaigns])
        
        # Add action buttons
        st.dataframe(
            campaigns_df[['id', 'name', 'subject', 'status', 'updated_at']],
            column_config={
                "id": st.column_config.NumberColumn("ID"),
                "name": st.column_config.TextColumn("Name"),
                "subject": st.column_config.TextColumn("Subject"),
                "status": st.column_config.TextColumn("Status"),
                "updated_at": st.column_config.DatetimeColumn("Last Updated"),
            },
            hide_index=True
        )
        
        # Campaign actions
        st.subheader("Campaign Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            campaign_to_edit = st.selectbox(
                "Select a campaign to manage:",
                options=[c['id'] for c in campaigns],
                format_func=lambda x: next((c['name'] for c in campaigns if c['id'] == x), ""),
                key="campaign_select_edit"
            )
        
        with col2:
            if st.button("✏️ Edit Campaign", key="edit_campaign_btn"):
                st.session_state.campaign_id = campaign_to_edit
                st.session_state.campaign_view = "edit"
                st.rerun()
        
        with col3:
            if st.button("🚀 Send Campaign", key="send_campaign_btn"):
                st.session_state.campaign_id = campaign_to_edit
                st.session_state.campaign_view = "send"
                st.rerun()
        
        # Duplicate or Delete options
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Duplicate Selected Campaign", key="duplicate_campaign"):
                selected_campaign = db.get_campaign_by_id(campaign_to_edit)
                if selected_campaign:
                    new_name = f"{selected_campaign['name']} (Copy)"
                    # Check if the name already exists
                    try:
                        new_id = db.add_campaign(
                            name=new_name,
                            subject=selected_campaign['subject'],
                            body_html=selected_campaign['body_html'],
                            body_text=selected_campaign['body_text'],
                            list_id=selected_campaign['list_id'],
                            smtp_config_id=selected_campaign['smtp_config_id'],
                            template_id=selected_campaign['template_id']
                        )
                        st.success(f"Campaign duplicated successfully with ID: {new_id}")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error duplicating campaign: {str(e)}")
        
        with col2:
            if st.button("❌ Delete Selected Campaign", key="delete_campaign"):
                if st.session_state.get("confirm_delete") != campaign_to_edit:
                    st.session_state.confirm_delete = campaign_to_edit
                    st.warning("Click the button again to confirm deletion.")
                else:
                    # User confirmed deletion
                    db.delete_campaign(campaign_to_edit)
                    st.success("Campaign deleted successfully!")
                    st.session_state.confirm_delete = None
                    time.sleep(1)
                    st.rerun()
    else:
        st.info("No campaigns found. Create your first campaign using the button above.")


elif st.session_state.campaign_view == "create":
    # Form for creating a new campaign
    st.subheader("Create New Campaign")
    
    with st.form("create_campaign_form"):
        campaign_name = st.text_input("Campaign Name", placeholder="Summer Sale 2023")
        
        # Get list of templates
        templates = db.get_email_templates()
        template_options = [("0", "No template - start from scratch")] + [(str(t['id']), t['name']) for t in templates]
        
        template_id = st.selectbox(
            "Select a Template",
            options=[t[0] for t in template_options],
            format_func=lambda x: next((t[1] for t in template_options if t[0] == x), ""),
            key="template_select"
        )
        
        # Get recipient lists
        recipient_lists = db.get_recipient_lists()
        recipient_list_options = [("0", "None - select later")] + [(str(rl['id']), rl['name']) for rl in recipient_lists]
        
        recipient_list_id = st.selectbox(
            "Select Recipient List",
            options=[rl[0] for rl in recipient_list_options],
            format_func=lambda x: next((rl[1] for rl in recipient_list_options if rl[0] == x), ""),
            key="recipient_list_select"
        )
        
        # Get SMTP configurations
        smtp_configs = db.get_smtp_configs()
        smtp_config_options = [("0", "None - select later")] + [(str(sc['id']), sc['profile_name']) for sc in smtp_configs]
        
        smtp_config_id = st.selectbox(
            "Select SMTP Configuration",
            options=[sc[0] for sc in smtp_config_options],
            format_func=lambda x: next((sc[1] for sc in smtp_config_options if sc[0] == x), ""),
            key="smtp_config_select"
        )
        
        submit_button = st.form_submit_button("Create Campaign")
        
        if submit_button:
            if not campaign_name:
                st.error("Campaign name is required.")
            else:
                try:
                    # Prepare template data if selected
                    selected_template = None
                    if template_id != "0":
                        selected_template = db.get_email_template_by_id(int(template_id))
                    
                    # Create the campaign
                    campaign_data = {
                        "name": campaign_name,
                        "subject": selected_template['subject'] if selected_template else "",
                        "body_html": selected_template['body_html'] if selected_template else "",
                        "body_text": "",
                        "list_id": int(recipient_list_id) if recipient_list_id != "0" else None,
                        "smtp_config_id": int(smtp_config_id) if smtp_config_id != "0" else None,
                        "template_id": int(template_id) if template_id != "0" else None
                    }
                    
                    new_campaign_id = db.add_campaign(**campaign_data)
                    
                    if new_campaign_id:
                        st.success(f"Campaign '{campaign_name}' created successfully!")
                        # Set the campaign ID for sending
                        st.session_state.campaign_id = new_campaign_id
                        st.session_state.campaign_view = "send"
                        st.rerun()
                    else:
                        st.error("Failed to create campaign. Please try again.")
                except Exception as e:
                    st.error(f"Error creating campaign: {str(e)}")
    
    # Cancel button
    if st.button("Cancel", key="cancel_create"):
        reset_campaign_view()
        st.rerun()


elif st.session_state.campaign_view == "edit" and st.session_state.campaign_id:
    # Form for editing an existing campaign
    campaign = db.get_campaign_by_id(st.session_state.campaign_id)
    
    if not campaign:
        st.error("Campaign not found. Please select another campaign.")
        reset_campaign_view()
        st.rerun()
    
    st.subheader(f"Edit Campaign: {campaign['name']}")
    
    tab1, tab2, tab3 = st.tabs(["Campaign Details", "Email Content", "Settings"])
    
    with tab1:
        # Campaign basic details
        with st.form("edit_campaign_details_form"):
            campaign_name = st.text_input("Campaign Name", value=campaign['name'])
            campaign_subject = st.text_input("Email Subject", value=campaign['subject'] or "")
            
            # Recipient list selection
            recipient_lists = db.get_recipient_lists()
            recipient_list_options = [("0", "None - select later")] + [(str(rl['id']), rl['name']) for rl in recipient_lists]
            
            current_list_id = str(campaign['list_id']) if campaign['list_id'] else "0"
            recipient_list_id = st.selectbox(
                "Select Recipient List",
                options=[rl[0] for rl in recipient_list_options],
                format_func=lambda x: next((rl[1] for rl in recipient_list_options if rl[0] == x), ""),
                key="edit_recipient_list_select",
                index=next((i for i, rl in enumerate(recipient_list_options) if rl[0] == current_list_id), 0)
            )
            
            # If a list is selected, show preview of recipients
            if recipient_list_id != "0":
                recipients = db.get_recipients_by_list(int(recipient_list_id))
                if recipients:
                    st.write(f"This list contains {len(recipients)} recipients")
                    if st.checkbox("Preview Recipients"):
                        recipients_df = pd.DataFrame([dict(r) for r in recipients])
                        display_cols = ['email', 'name']
                        st.dataframe(recipients_df[display_cols].head(10), hide_index=True)
                        if len(recipients) > 10:
                            st.info(f"Showing 10 of {len(recipients)} recipients")
                else:
                    st.warning("This list contains no recipients")
            
            submit_button = st.form_submit_button("Save Campaign Details")
            
            if submit_button:
                if not campaign_name:
                    st.error("Campaign name is required.")
                else:
                    try:
                        # Update campaign details
                        updates = {
                            "name": campaign_name,
                            "subject": campaign_subject,
                            "list_id": int(recipient_list_id) if recipient_list_id != "0" else None
                        }
                        
                        db.update_campaign(st.session_state.campaign_id, **updates)
                        st.success("Campaign details updated successfully!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error updating campaign: {str(e)}")
    
    with tab2:
        # Email content editor
        with st.form("edit_campaign_content_form"):
            # Template selection
            templates = db.get_email_templates()
            template_options = [("0", "No template - use current content")] + [(str(t['id']), t['name']) for t in templates]
            
            st.write("Select a template to start with (will replace current content)")
            template_id = st.selectbox(
                "Email Template",
                options=[t[0] for t in template_options],
                format_func=lambda x: next((t[1] for t in template_options if t[0] == x), ""),
                key="edit_template_select"
            )
            
            # Current content
            st.write("Email Body (HTML)")
            email_body = st.text_area(
                "HTML Content",
                value=campaign['body_html'] or "",
                height=400,
                help="You can use HTML to format your email and placeholders like {{recipient_name}}"
            )
            
            # Preview button in form
            preview_col1, preview_col2 = st.columns(2)
            with preview_col1:
                preview_pressed = st.form_submit_button("Preview Email")
            with preview_col2:
                submit_button = st.form_submit_button("Save Email Content")
            
            if preview_pressed:
                # Show preview
                st.subheader("Email Preview")
                st.write("This is how your email might look with sample data:")
                
                # Sample data for preview
                sample_data = {
                    'recipient_email': 'sample@example.com',
                    'recipient_name': 'Sample User',
                    'unsubscribe_link': '#',
                    'view_in_browser_link': '#',
                    'current_year': datetime.now().year,
                    'sender_name': 'Your Company',
                    'company_name': 'Your Company',
                    'custom1': 'Custom Field 1',
                    'custom2': 'Custom Field 2',
                    'custom3': 'Custom Field 3',
                    'custom4': 'Custom Field 4',
                    'custom5': 'Custom Field 5'
                }
                
                # Render with sample data
                preview_html = Helpers.render_template(email_body, sample_data)
                st.components.v1.html(preview_html, height=600, scrolling=True)
            
            if submit_button:
                try:
                    updates = {}
                    
                    # If a template was selected, get its content
                    if template_id != "0":
                        selected_template = db.get_email_template_by_id(int(template_id))
                        if selected_template:
                            updates["body_html"] = selected_template['body_html']
                            updates["subject"] = selected_template['subject']
                            updates["template_id"] = int(template_id)
                    else:
                        # Use the edited content
                        updates["body_html"] = email_body
                    
                    # Update campaign
                    db.update_campaign(st.session_state.campaign_id, **updates)
                    st.success("Email content updated successfully!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error updating email content: {str(e)}")
    
    with tab3:
        # SMTP and delivery settings
        with st.form("edit_campaign_settings_form"):
            # SMTP configuration
            smtp_configs = db.get_smtp_configs()
            smtp_config_options = [("0", "None - select later")] + [(str(sc['id']), sc['profile_name']) for sc in smtp_configs]
            
            current_smtp_id = str(campaign['smtp_config_id']) if campaign['smtp_config_id'] else "0"
            smtp_config_id = st.selectbox(
                "Select SMTP Configuration",
                options=[sc[0] for sc in smtp_config_options],
                format_func=lambda x: next((sc[1] for sc in smtp_config_options if sc[0] == x), ""),
                key="edit_smtp_config_select",
                index=next((i for i, sc in enumerate(smtp_config_options) if sc[0] == current_smtp_id), 0)
            )
            
            # Throttle rate
            throttle_rate = st.number_input(
                "Throttle Rate (emails per minute)",
                min_value=1,
                max_value=100,
                value=campaign['throttle_rate'] or 10,
                help="Limit how many emails are sent per minute to avoid being flagged as spam"
            )
            
            # Scheduling
            enable_scheduling = st.checkbox(
                "Schedule Campaign",
                help="Set a future date and time to send this campaign"
            )
            
            scheduled_date = None
            if enable_scheduling:
                scheduled_date = st.date_input(
                    "Scheduled Date",
                    value=datetime.now().date() + timedelta(days=1),
                    min_value=datetime.now().date()
                )
                scheduled_time = st.time_input(
                    "Scheduled Time",
                    value=datetime.now().time()
                )
                scheduled_datetime = datetime.combine(scheduled_date, scheduled_time)
                st.write(f"Campaign will be sent at: {scheduled_datetime.strftime('%Y-%m-%d %H:%M')}")
            
            submit_button = st.form_submit_button("Save Campaign Settings")
            
            if submit_button:
                try:
                    # Update campaign settings
                    updates = {
                        "smtp_config_id": int(smtp_config_id) if smtp_config_id != "0" else None,
                        "throttle_rate": throttle_rate,
                        "scheduled_date": scheduled_datetime.strftime('%Y-%m-%d %H:%M:%S') if enable_scheduling else None
                    }
                    
                    db.update_campaign(st.session_state.campaign_id, **updates)
                    st.success("Campaign settings updated successfully!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error updating campaign settings: {str(e)}")
    
    # Back button
    if st.button("Back to Campaign List", key="back_to_list"):
        reset_campaign_view()
        st.rerun()


elif st.session_state.campaign_view == "send" and st.session_state.campaign_id:
    # Send campaign interface
    campaign = db.get_campaign_by_id(st.session_state.campaign_id)
    
    if not campaign:
        st.error("Campaign not found. Please select another campaign.")
        reset_campaign_view()
        st.rerun()
    
    st.subheader(f"Send Campaign: {campaign['name']}")
    
    # Verify campaign is ready to send
    missing_requirements = []
    
    if not campaign['subject']:
        missing_requirements.append("- Email subject is missing")
    
    if not campaign['body_html']:
        missing_requirements.append("- Email content is missing")
    
    if not campaign['list_id']:
        missing_requirements.append("- No recipient list selected")
    else:
        recipients = db.get_recipients_by_list(campaign['list_id'])
        if not recipients or len(recipients) == 0:
            missing_requirements.append("- Selected recipient list is empty")
    
    if not campaign['smtp_config_id']:
        missing_requirements.append("- No SMTP configuration selected")
    
    # Display campaign summary and confirm sending
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("Campaign Details:")
        st.write(f"**Name:** {campaign['name']}")
        st.write(f"**Subject:** {campaign['subject']}")
        
        if campaign['list_id']:
            recipient_list = db.get_recipient_list_by_id(campaign['list_id'])
            recipients = db.get_recipients_by_list(campaign['list_id'])
            st.write(f"**Recipient List:** {recipient_list['name']} ({len(recipients)} recipients)")
        else:
            st.write("**Recipient List:** None selected")
        
        if campaign['smtp_config_id']:
            smtp_config = db.get_smtp_config_by_id(campaign['smtp_config_id'])
            st.write(f"**SMTP Configuration:** {smtp_config['profile_name']}")
            st.write(f"**Sender:** {smtp_config['sender_name']} <{smtp_config['sender_email']}>")
        else:
            st.write("**SMTP Configuration:** None selected")
    
    with col2:
        if missing_requirements:
            st.error("Unable to send campaign. Please fix the following issues:")
            for req in missing_requirements:
                st.write(req)
            
            if st.button("Edit Campaign", key="edit_from_send"):
                st.session_state.campaign_view = "edit"
                st.rerun()
        else:
            st.success("Campaign is ready to send! 🚀")
            
            # Final confirmation to send
            send_now = st.button("Send Campaign Now", key="send_campaign_confirm")
            
            if send_now:
                # Get the required data
                smtp_config = db.get_smtp_config_by_id(campaign['smtp_config_id'])
                recipients = db.get_recipients_by_list(campaign['list_id'])
                
                # Initialize email sender
                email_sender = EmailSender(dict(smtp_config))
                
                # Send the campaign (in the real app, this should probably be async)
                st.info("Sending campaign...")
                success_count, failure_count, error = email_sender.send_campaign(
                    dict(campaign),
                    [dict(r) for r in recipients],
                    db,
                    throttle_rate=campaign['throttle_rate']
                )
                
                # Update campaign status
                db.update_campaign(campaign['id'], status="sent" if failure_count == 0 else "partial")
                
                # Show results
                if success_count > 0:
                    st.success(f"Successfully sent to {success_count} recipients!")
                    
                if failure_count > 0:
                    st.warning(f"Failed to send to {failure_count} recipients.")
                    if error:
                        st.error(f"Error: {error}")
                
                # Option to view results
                st.info("View detailed campaign results in the Analytics section.")
                if st.button("View Analytics", key="view_analytics"):
                    # In a real app, would set parameters to view this campaign's analytics
                    st.switch_page("pages/4_Analytics.py")
    
    # Back button
    if st.button("Back to Campaign List", key="back_to_list_from_send"):
        reset_campaign_view()
        st.rerun()


# Footer
st.markdown("---")
st.markdown("DominionMailer v0.1.0 - *Design like a creator. Deliver like a machine.*")
