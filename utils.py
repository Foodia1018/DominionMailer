import re
import hashlib
import time
import string
import random
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate, make_msgid

class Helpers:
    @staticmethod
    def is_valid_email(email):
        """Validate email using regex"""
        regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(regex, email) is not None
    
    @staticmethod
    def extract_domain(email):
        """Extract domain from email address"""
        if "@" in email:
            return email.split("@")[1].lower()
        return None
    
    @staticmethod
    def generate_unsubscribe_link(base_url, email_hash):
        """Generate unsubscribe link (placeholder implementation)"""
        return f"{base_url}/unsubscribe?id={email_hash}"
    
    @staticmethod
    def generate_view_in_browser_link(base_url, campaign_id, email_hash):
        """Generate view in browser link (placeholder implementation)"""
        return f"{base_url}/view?cid={campaign_id}&eid={email_hash}"
    
    @staticmethod
    def get_current_timestamp():
        """Get formatted current timestamp"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def hash_string(s, algorithm='sha256'):
        """Hash a string using the specified algorithm"""
        h = hashlib.new(algorithm)
        h.update(s.encode('utf-8'))
        return h.hexdigest()
    
    @staticmethod
    def validate_and_process_csv(df):
        """
        Validate and process CSV data for recipient import
        
        Args:
            df: Pandas DataFrame with CSV data
            
        Returns:
            tuple: (is_valid, processed_data or error_message)
        """
        required_cols = ['email']
        
        # Check for required columns
        if not all(col in df.columns for col in required_cols):
            return False, "CSV must contain at least an 'email' column"
        
        # Initialize processed data list
        processed_data = []
        invalid_emails = []
        
        # Process each row
        for i, row in df.iterrows():
            email = row['email'].strip() if isinstance(row['email'], str) else str(row['email']).strip()
            
            # Validate email
            if not Helpers.is_valid_email(email):
                invalid_emails.append(f"Row {i+2}: {email}")
                continue
            
            # Create recipient record
            recipient = {
                'email': email,
                'domain': Helpers.extract_domain(email)
            }
            
            # Add optional fields if present
            optional_fields = ['name', 'custom1', 'custom2', 'custom3', 'custom4', 'custom5']
            for field in optional_fields:
                if field in df.columns:
                    recipient[field] = row[field] if not pd.isna(row[field]) else None
            
            processed_data.append(recipient)
        
        # Return results
        if invalid_emails:
            return False, f"Found {len(invalid_emails)} invalid email(s):\n" + "\n".join(invalid_emails[:10]) + (
                f"\n... and {len(invalid_emails) - 10} more" if len(invalid_emails) > 10 else ""
            )
        
        if not processed_data:
            return False, "No valid emails found in the CSV"
        
        return True, processed_data
    
    @staticmethod
    def render_template(template, data):
        """
        Render an email template with the provided data
        
        Args:
            template: HTML template with placeholders
            data: Dictionary of placeholder values
            
        Returns:
            rendered template with placeholders replaced
        """
        rendered = template
        for key, value in data.items():
            placeholder = "{{" + key + "}}"
            rendered = rendered.replace(placeholder, str(value))
        return rendered
