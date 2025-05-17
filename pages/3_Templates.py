import streamlit as st
from css.templates import get_templates
from utils import Helpers
from datetime import datetime

st.set_page_config(
    page_title="Email Templates | DominionMailer",
    page_icon="📝",
    layout="wide"
)

# Check if database is initialized
if "db" not in st.session_state:
    st.error("Database not initialized. Please restart the application.")
    st.stop()

db = st.session_state.db

# Initialize session state variables
if "template_id" not in st.session_state:
    st.session_state.template_id = None

if "template_view" not in st.session_state:
    st.session_state.template_view = "list"  # list, create, edit

def reset_template_view():
    st.session_state.template_view = "list"
    st.session_state.template_id = None

# Header
st.title("📝 Email Templates")

# Template gallery - displayed at the top of the page in list view
if st.session_state.template_view == "list":
    # Show template image gallery
    st.header("Template Gallery")
    
    # Display available templates
    template_data = get_templates()
    
    # Create columns for template gallery
    cols = st.columns(3)
    
    for i, template in enumerate(template_data):
        with cols[i % 3]:
            st.subheader(template["name"])
            st.image(template["image_url"], use_column_width=True)
            st.markdown(template["description"])
            
            if st.button(f"Use Template", key=f"use_template_{i}"):
                # Create a new template based on this gallery template
                try:
                    new_template_id = db.add_email_template(
                        name=f"{template['name']} {datetime.now().strftime('%Y-%m-%d')}",
                        subject=template["subject"],
                        body_html=template["html"]
                    )
                    
                    if new_template_id:
                        st.session_state.template_id = new_template_id
                        st.session_state.template_view = "edit"
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"Error creating template: {str(e)}")
    
    # User templates
    st.header("Your Templates")
    
    # Create button for a completely new template
    if st.button("➕ Create New Template", key="new_template"):
        st.session_state.template_view = "create"
        st.rerun()
    
    # Get all templates from database
    templates = db.get_email_templates()
    
    if templates and len(templates) > 0:
        # Create columns for user templates
        cols = st.columns(3)
        
        for i, template in enumerate(templates):
            with cols[i % 3]:
                st.subheader(template["name"])
                
                # Preview button
                if st.button(f"Preview", key=f"preview_{template['id']}"):
                    st.session_state.template_id = template['id']
                    st.session_state.template_view = "preview"
                    st.rerun()
                
                # Edit button
                if st.button(f"Edit", key=f"edit_{template['id']}"):
                    st.session_state.template_id = template['id']
                    st.session_state.template_view = "edit"
                    st.rerun()
                
                # Delete button
                if st.button(f"Delete", key=f"delete_{template['id']}"):
                    if st.session_state.get("confirm_delete") != template['id']:
                        st.session_state.confirm_delete = template['id']
                        st.warning("Click the button again to confirm deletion.")
                    else:
                        # User confirmed deletion
                        db.delete_email_template(template['id'])
                        st.success("Template deleted successfully!")
                        st.session_state.confirm_delete = None
                        st.rerun()
    else:
        st.info("No custom templates found. Create your first template using the button above.")

elif st.session_state.template_view == "create":
    # Form for creating a new template
    st.subheader("Create New Email Template")
    
    with st.form("create_template_form"):
        template_name = st.text_input("Template Name", placeholder="Monthly Newsletter")
        template_subject = st.text_input("Default Subject Line", placeholder="{{company_name}} Newsletter - {{newsletter_date}}")
        
        st.write("Email Content (HTML)")
        st.markdown("You can use placeholders like `{{recipient_name}}` that will be replaced with actual data when sending emails.")
        
        # Common placeholders help
        with st.expander("Available Placeholders"):
            st.markdown("""
            - `{{recipient_email}}` - Recipient's email address
            - `{{recipient_name}}` - Recipient's name
            - `{{unsubscribe_link}}` - Link to unsubscribe
            - `{{view_in_browser_link}}` - Link to view email in browser
            - `{{current_year}}` - Current year (e.g., 2023)
            - `{{sender_name}}` - Name of the sender
            - `{{company_name}}` - Your company name
            - `{{custom1}}` through `{{custom5}}` - Custom fields from recipient data
            """)
        
        # Start with a simple template
        default_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 0; }
                .container { width: 100%; max-width: 600px; margin: 0 auto; }
                .header { background-color: #5E81AC; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; }
                .footer { background-color: #f5f5f5; padding: 10px; text-align: center; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{{company_name}}</h1>
                </div>
                <div class="content">
                    <h2>Hello {{recipient_name}},</h2>
                    <p>This is a sample email template. Replace this text with your own content.</p>
                    <p>Best regards,<br>{{sender_name}}</p>
                </div>
                <div class="footer">
                    <p>© {{current_year}} {{company_name}}. All rights reserved.</p>
                    <p><a href="{{unsubscribe_link}}">Unsubscribe</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        template_html = st.text_area("HTML Content", value=default_html, height=400)
        
        # Preview button and Submit button in a row
        col1, col2 = st.columns(2)
        
        with col1:
            preview_pressed = st.form_submit_button("Preview")
        
        with col2:
            submit_button = st.form_submit_button("Create Template")
        
        if preview_pressed:
            # Show preview with placeholder data
            st.subheader("Template Preview")
            
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
            preview_html = Helpers.render_template(template_html, sample_data)
            st.components.v1.html(preview_html, height=600, scrolling=True)
        
        if submit_button:
            if not template_name:
                st.error("Template name is required.")
            elif not template_subject:
                st.error("Template subject is required.")
            elif not template_html:
                st.error("Template HTML content is required.")
            else:
                try:
                    new_template_id = db.add_email_template(
                        name=template_name,
                        subject=template_subject,
                        body_html=template_html
                    )
                    
                    if new_template_id:
                        st.success(f"Template '{template_name}' created successfully!")
                        # Set the template ID for editing
                        st.session_state.template_id = new_template_id
                        st.session_state.template_view = "edit"
                        st.rerun()
                    else:
                        st.error("Failed to create template. Please try again.")
                except Exception as e:
                    st.error(f"Error creating template: {str(e)}")
    
    # Cancel button
    if st.button("Cancel", key="cancel_create"):
        reset_template_view()
        st.rerun()

elif st.session_state.template_view == "edit" and st.session_state.template_id:
    # Form for editing an existing template
    template = db.get_email_template_by_id(st.session_state.template_id)
    
    if not template:
        st.error("Template not found. Please select another template.")
        reset_template_view()
        st.rerun()
    
    st.subheader(f"Edit Template: {template['name']}")
    
    with st.form("edit_template_form"):
        template_name = st.text_input("Template Name", value=template['name'])
        template_subject = st.text_input("Default Subject Line", value=template['subject'] or "")
        
        st.write("Email Content (HTML)")
        st.markdown("You can use placeholders like `{{recipient_name}}` that will be replaced with actual data when sending emails.")
        
        # Common placeholders help
        with st.expander("Available Placeholders"):
            st.markdown("""
            - `{{recipient_email}}` - Recipient's email address
            - `{{recipient_name}}` - Recipient's name
            - `{{unsubscribe_link}}` - Link to unsubscribe
            - `{{view_in_browser_link}}` - Link to view email in browser
            - `{{current_year}}` - Current year (e.g., 2023)
            - `{{sender_name}}` - Name of the sender
            - `{{company_name}}` - Your company name
            - `{{custom1}}` through `{{custom5}}` - Custom fields from recipient data
            """)
        
        template_html = st.text_area("HTML Content", value=template['body_html'] or "", height=400)
        
        # Preview button and Submit button in a row
        col1, col2 = st.columns(2)
        
        with col1:
            preview_pressed = st.form_submit_button("Preview")
        
        with col2:
            submit_button = st.form_submit_button("Save Template")
        
        if preview_pressed:
            # Show preview with placeholder data
            st.subheader("Template Preview")
            
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
            preview_html = Helpers.render_template(template_html, sample_data)
            st.components.v1.html(preview_html, height=600, scrolling=True)
        
        if submit_button:
            if not template_name:
                st.error("Template name is required.")
            elif not template_subject:
                st.error("Template subject is required.")
            elif not template_html:
                st.error("Template HTML content is required.")
            else:
                try:
                    db.update_email_template(
                        st.session_state.template_id,
                        name=template_name,
                        subject=template_subject,
                        body_html=template_html
                    )
                    
                    st.success(f"Template '{template_name}' updated successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error updating template: {str(e)}")
    
    # Back button
    if st.button("Back to Templates", key="back_to_list"):
        reset_template_view()
        st.rerun()

elif st.session_state.template_view == "preview" and st.session_state.template_id:
    # Preview of a template
    template = db.get_email_template_by_id(st.session_state.template_id)
    
    if not template:
        st.error("Template not found. Please select another template.")
        reset_template_view()
        st.rerun()
    
    st.subheader(f"Preview: {template['name']}")
    st.write(f"Subject: {template['subject']}")
    
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
        'custom5': 'Custom Field 5',
        'newsletter_date': datetime.now().strftime('%B %Y'),
        'greeting_text': 'Welcome to our monthly newsletter!',
        'article1_title': 'Feature Article',
        'article1_content': 'This is the content of our feature article.',
        'article2_title': 'Company Updates',
        'article2_content': 'Here are the latest updates from our company.',
        'offer_headline': 'Special Discount!',
        'offer_details': 'Get 20% off your next purchase.',
        'promo_code': 'DISCOUNT20',
        'offer_expiry_details': 'Offer valid until the end of the month.',
        'cta_text': 'Shop Now',
        'cta_link': '#',
        'intro_text': 'We have a special offer just for you!'
    }
    
    # Render with sample data
    preview_html = Helpers.render_template(template['body_html'], sample_data)
    
    # Display the rendered HTML
    st.components.v1.html(preview_html, height=600, scrolling=True)
    
    # Action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Edit Template", key="edit_from_preview"):
            st.session_state.template_view = "edit"
            st.rerun()
    
    with col2:
        if st.button("Back to Templates", key="back_from_preview"):
            reset_template_view()
            st.rerun()


# Footer
st.markdown("---")
st.markdown("DominionMailer v0.1.0 - *Design like a creator. Deliver like a machine.*")
