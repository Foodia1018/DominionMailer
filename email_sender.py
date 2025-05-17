import smtplib
import streamlit as st
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate, make_msgid
import time
from datetime import datetime
from utils import Helpers

class EmailSender:
    def __init__(self, smtp_config):
        """
        Initialize EmailSender with SMTP configuration
        
        Args:
            smtp_config: Dictionary containing SMTP configuration
        """
        self.host = smtp_config['host']
        self.port = smtp_config['port']
        self.username = smtp_config['username']
        self.password = smtp_config['password']
        self.use_tls = smtp_config['use_tls']
        self.use_ssl = smtp_config.get('use_ssl', False)
        self.timeout = smtp_config.get('timeout', 30)
        self.sender_email = smtp_config['sender_email']
        self.sender_name = smtp_config['sender_name']
    
    def send_test_email(self, recipient_email, subject, html_content, text_content=None):
        """
        Send a test email to verify SMTP configuration
        
        Args:
            recipient_email: Email address of the recipient
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text content (optional)
            
        Returns:
            tuple: (success, message)
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.sender_name} <{self.sender_email}>"
            msg['To'] = recipient_email
            msg['Date'] = formatdate(localtime=True)
            msg['Message-ID'] = make_msgid(domain=self.sender_email.split('@')[1])
            
            # Add text part if provided
            if text_content:
                msg.attach(MIMEText(text_content, 'plain'))
            
            # Add HTML part
            msg.attach(MIMEText(html_content, 'html'))
            
            # Connect to SMTP server
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.host, self.port, timeout=self.timeout)
            else:
                server = smtplib.SMTP(self.host, self.port, timeout=self.timeout)
                
            if self.use_tls:
                server.starttls()
            
            # Login and send
            server.login(self.username, self.password)
            server.sendmail(self.sender_email, recipient_email, msg.as_string())
            server.quit()
            
            return True, "Test email sent successfully!"
            
        except Exception as e:
            return False, f"Error sending test email: {str(e)}"
    
    def send_campaign(self, campaign, recipients, db, base_url="http://example.com", throttle_rate=10):
        """
        Send a campaign to multiple recipients
        
        Args:
            campaign: Campaign data dictionary
            recipients: List of recipient dictionaries
            db: Database manager instance for tracking
            base_url: Base URL for unsubscribe links
            throttle_rate: Number of emails per minute (throttling)
            
        Returns:
            tuple: (success_count, failure_count, error_message)
        """
        if not campaign or not recipients:
            return 0, 0, "No campaign or recipients provided"
        
        success_count = 0
        failure_count = 0
        last_error = None
        
        # Calculate delay between emails based on throttle rate
        delay = 60 / max(1, throttle_rate)
        
        # Create progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Connect to SMTP server
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.host, self.port, timeout=self.timeout)
            else:
                server = smtplib.SMTP(self.host, self.port, timeout=self.timeout)
                
            if self.use_tls:
                server.starttls()
            
            # Login to SMTP server
            server.login(self.username, self.password)
            
            # Process each recipient
            for i, recipient in enumerate(recipients):
                # Update progress
                progress = int(100 * (i / len(recipients)))
                progress_bar.progress(progress)
                status_text.text(f"Sending: {i+1}/{len(recipients)} ({progress}%)")
                
                try:
                    # Create personalized message
                    msg = self._create_personalized_message(campaign, recipient, base_url)
                    
                    # Send the email
                    server.sendmail(self.sender_email, recipient['email'], msg.as_string())
                    
                    # Record success in tracking table
                    db.add_email_tracking(campaign['id'], recipient['id'], 'sent')
                    success_count += 1
                    
                    # Throttle sending
                    if i < len(recipients) - 1:  # Don't sleep after the last email
                        time.sleep(delay)
                        
                except Exception as e:
                    # Record failure in tracking table
                    db.add_email_tracking(campaign['id'], recipient['id'], 'failed', str(e))
                    failure_count += 1
                    last_error = str(e)
            
            # Close the connection
            server.quit()
            
            # Complete progress bar
            progress_bar.progress(100)
            status_text.text(f"Completed: {success_count} sent, {failure_count} failed")
            
            return success_count, failure_count, last_error
            
        except Exception as e:
            return success_count, failure_count, str(e)
    
    def _create_personalized_message(self, campaign, recipient, base_url):
        """
        Create a personalized email message for a recipient
        
        Args:
            campaign: Campaign data dictionary
            recipient: Recipient data dictionary
            base_url: Base URL for unsubscribe links
            
        Returns:
            MIMEMultipart message object
        """
        # Create message
        msg = MIMEMultipart('alternative')
        
        # Generate unique hash for this recipient
        email_hash = Helpers.hash_string(recipient['email'])
        
        # Add basic headers
        msg['Subject'] = campaign['subject']
        msg['From'] = f"{self.sender_name} <{self.sender_email}>"
        msg['To'] = recipient['email']
        msg['Date'] = formatdate(localtime=True)
        msg['Message-ID'] = make_msgid(domain=self.sender_email.split('@')[1])
        
        # Process HTML content
        html_content = campaign['body_html']
        
        # Replace placeholders with recipient data
        template_data = {
            'recipient_email': recipient['email'],
            'recipient_name': recipient.get('name', 'Valued Customer'),
            'unsubscribe_link': Helpers.generate_unsubscribe_link(base_url, email_hash),
            'view_in_browser_link': Helpers.generate_view_in_browser_link(base_url, campaign['id'], email_hash),
            'current_year': datetime.now().year,
            'sender_name': self.sender_name,
            'company_name': self.sender_name
        }
        
        # Add custom fields if present
        for i in range(1, 6):
            field_name = f'custom{i}'
            if field_name in recipient and recipient[field_name]:
                template_data[field_name] = recipient[field_name]
        
        # Render the template
        personalized_html = Helpers.render_template(html_content, template_data)
        
        # Create a simple text version if needed
        text_content = "Please view this email in a modern email client to see the content."
        
        # Attach parts
        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(personalized_html, 'html'))
        
        return msg
