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
        """Initialize EmailSender with SMTP configuration"""
        self.host = smtp_config['host']
        self.port = smtp_config['port']
        self.username = smtp_config['username']
        self.password = smtp_config['password']
        self.use_tls = smtp_config['use_tls']
        self.use_ssl = smtp_config.get('use_ssl', False)
        self.timeout = smtp_config.get('timeout', 30)
        self.sender_email = smtp_config['sender_email']
        self.sender_name = smtp_config['sender_name']

    @staticmethod
    def get_next_smtp_config(db, current_config_id=None):
        """Get next available SMTP configuration based on rotation order and limits"""
        configs = db.execute_query(
            """
            SELECT * FROM smtp_configs 
            WHERE (
                SELECT COUNT(*) FROM email_tracking 
                WHERE sent_at > date('now', '-1 day') 
                AND smtp_config_id = smtp_configs.id
            ) < daily_limit
            ORDER BY CASE WHEN rotation_order = 0 THEN 999999 ELSE rotation_order END
            """, 
            fetch_all=True
        )

        if not configs:
            return None

        if current_config_id:
            # Find next config after current
            for i, config in enumerate(configs):
                if config['id'] == current_config_id and i + 1 < len(configs):
                    return configs[i + 1]

        return configs[0]

    
    def send_test_email(self, recipient_email, subject, html_content, text_content=None):
        """Send a test email to verify SMTP configuration"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.sender_name} <{self.sender_email}>"
            msg['To'] = recipient_email
            msg['Date'] = formatdate(localtime=True)
            msg['Message-ID'] = make_msgid(domain=self.sender_email.split('@')[1])

            if text_content:
                msg.attach(MIMEText(text_content, 'plain'))

            msg.attach(MIMEText(html_content, 'html'))

            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.host, self.port, timeout=self.timeout)
            else:
                server = smtplib.SMTP(self.host, self.port, timeout=self.timeout)

            if self.use_tls:
                server.starttls()

            server.login(self.username, self.password)
            server.sendmail(self.sender_email, recipient_email, msg.as_string())
            server.quit()

            return True, "Test email sent successfully!"

        except Exception as e:
            return False, f"Error sending test email: {str(e)}"

    def send_campaign(self, campaign, recipients, db, base_url="http://example.com", throttle_rate=10):
        """Send a campaign to multiple recipients using SMTP rotation"""
        if not campaign or not recipients:
            return 0, 0, "No campaign or recipients provided"

        success_count = 0
        failure_count = 0
        last_error = None
        delay = 60 / max(1, throttle_rate)

        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            server = None
            for i, recipient in enumerate(recipients):
                progress = int(100 * (i / len(recipients)))
                progress_bar.progress(progress)
                status_text.text(f"Sending: {i+1}/{len(recipients)} ({progress}%)")

                try:
                    msg = self._create_personalized_message(campaign, recipient, base_url)
                    if not server:
                        if self.use_ssl:
                            server = smtplib.SMTP_SSL(self.host, self.port, timeout=self.timeout)
                        else:
                            server = smtplib.SMTP(self.host, self.port, timeout=self.timeout)
                            if self.use_tls:
                                server.starttls()
                        server.login(self.username, self.password)

                    server.sendmail(self.sender_email, recipient['email'], msg.as_string())
                    db.add_email_tracking(campaign['id'], recipient['id'], 'sent')
                    success_count += 1

                    if i < len(recipients) - 1:
                        time.sleep(delay)

                except Exception as e:
                    db.add_email_tracking(campaign['id'], recipient['id'], 'failed', str(e))
                    failure_count += 1
                    last_error = str(e)

            if server:
                server.quit()

            progress_bar.progress(100)
            status_text.text(f"Completed: {success_count} sent, {failure_count} failed")

            return success_count, failure_count, last_error

        except Exception as e:
            return success_count, failure_count, str(e)

    def _create_personalized_message(self, campaign, recipient, base_url):
        """Create a personalized email message for a recipient"""
        msg = MIMEMultipart('alternative')
        email_hash = Helpers.hash_string(recipient['email'])

        msg['Subject'] = campaign['subject']
        msg['From'] = f"{self.sender_name} <{self.sender_email}>"
        msg['To'] = recipient['email']
        msg['Date'] = formatdate(localtime=True)
        msg['Message-ID'] = make_msgid(domain=self.sender_email.split('@')[1])

        html_content = campaign['body_html']

        template_data = {
            'recipient_email': recipient['email'],
            'recipient_name': recipient.get('name', 'Valued Customer'),
            'unsubscribe_link': Helpers.generate_unsubscribe_link(base_url, email_hash),
            'view_in_browser_link': Helpers.generate_view_in_browser_link(base_url, campaign['id'], email_hash),
            'current_year': datetime.now().year,
            'sender_name': self.sender_name,
            'company_name': self.sender_name
        }

        for i in range(1, 6):
            field_name = f'custom{i}'
            if field_name in recipient and recipient[field_name]:
                template_data[field_name] = recipient[field_name]

        personalized_html = Helpers.render_template(html_content, template_data)
        text_content = "Please view this email in a modern email client to see the content."

        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(personalized_html, 'html'))

        return msg