import sqlite3
import time
import pandas as pd
import streamlit as st
from datetime import datetime

class DBManager:
    def __init__(self, db_name="dominion_mailer_data.db"):
        self.db_name = db_name
        self.create_tables()

    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row  # Access columns by name
        return conn

    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False, commit=False):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            if commit:
                conn.commit()
                result = cursor.lastrowid
            else:
                result = cursor.fetchone() if fetch_one else (cursor.fetchall() if fetch_all else cursor)
            return result
        except sqlite3.Error as e:
            st.error(f"Database error: {e}")
            st.error(f"Query: {query}")
            st.error(f"Params: {params}")
            return None
        finally:
            conn.close()

    def create_tables(self):
        # Campaigns Table
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                sender_id TEXT,
                subject TEXT,
                body_html TEXT,
                body_text TEXT,
                list_id INTEGER,
                smtp_config_id INTEGER,
                throttle_rate INTEGER DEFAULT 10,
                status TEXT DEFAULT 'draft',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                scheduled_date DATETIME,
                template_id INTEGER
            )
        """)
        
        # Recipient Lists Table
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS recipient_lists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Recipients Table
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS recipients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                list_id INTEGER NOT NULL,
                email TEXT NOT NULL,
                name TEXT,
                domain TEXT,
                custom1 TEXT, custom2 TEXT, custom3 TEXT, custom4 TEXT, custom5 TEXT,
                status TEXT DEFAULT 'active',
                added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(list_id, email),
                FOREIGN KEY (list_id) REFERENCES recipient_lists(id) ON DELETE CASCADE
            )
        """)
        
        # SMTP Configurations Table
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS smtp_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_name TEXT NOT NULL UNIQUE,
                host TEXT NOT NULL,
                port INTEGER NOT NULL,
                username TEXT,
                password TEXT,
                use_tls BOOLEAN DEFAULT TRUE,
                use_ssl BOOLEAN DEFAULT FALSE,
                timeout INTEGER DEFAULT 30,
                sender_email TEXT,
                sender_name TEXT
            )
        """)
        
        # Email Tracking Table
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS email_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER NOT NULL,
                recipient_id INTEGER NOT NULL,
                sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT,
                error_message TEXT,
                opened BOOLEAN DEFAULT FALSE,
                opened_at DATETIME,
                clicked BOOLEAN DEFAULT FALSE,
                clicked_at DATETIME,
                FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
                FOREIGN KEY (recipient_id) REFERENCES recipients(id) ON DELETE CASCADE
            )
        """)
        
        # Templates Table
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS email_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                subject TEXT,
                body_html TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Insert default SMTP config if none exists
        if not self.get_smtp_configs():
            self.add_smtp_config(
                profile_name="Default SMTP",
                host="smtp.example.com",
                port=587,
                username="user@example.com",
                password="password",
                use_tls=True,
                sender_email="sender@example.com",
                sender_name="DominionMailer"
            )
            
        # Insert default templates if none exist
        if not self.get_email_templates():
            # Simple template
            self.add_email_template(
                "Simple Announcement",
                "Important Announcement",
                """
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
                            <p>{{main_content}}</p>
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
            )
            
            # Newsletter template
            self.add_email_template(
                "Monthly Newsletter",
                "{{company_name}} - Monthly Newsletter",
                """
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 0; padding: 0; }
                        .container { width: 100%; max-width: 600px; margin: 0 auto; }
                        .header { background-color: #5E81AC; color: white; padding: 20px; text-align: center; }
                        .content { padding: 20px; }
                        .article { margin-bottom: 20px; }
                        .article h3 { color: #5E81AC; }
                        .footer { background-color: #f5f5f5; padding: 10px; text-align: center; font-size: 12px; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>{{company_name}} Newsletter</h1>
                            <p>{{newsletter_date}}</p>
                        </div>
                        <div class="content">
                            <h2>Hello {{recipient_name}},</h2>
                            <p>{{greeting_text}}</p>
                            
                            <div class="article">
                                <h3>{{article1_title}}</h3>
                                <p>{{article1_content}}</p>
                            </div>
                            
                            <div class="article">
                                <h3>{{article2_title}}</h3>
                                <p>{{article2_content}}</p>
                            </div>
                            
                            <p>Thank you for your continued support!</p>
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
            )
            
            # Promotional template
            self.add_email_template(
                "Special Offer",
                "Special Offer Inside! Limited Time Only",
                """
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 0; padding: 0; }
                        .container { width: 100%; max-width: 600px; margin: 0 auto; }
                        .header { background-color: #A3BE8C; color: white; padding: 20px; text-align: center; }
                        .content { padding: 20px; }
                        .offer { background-color: #EBCB8B; padding: 15px; text-align: center; margin: 20px 0; }
                        .offer h2 { color: #2E3440; }
                        .cta-button { display: inline-block; background-color: #5E81AC; color: white; padding: 15px 25px; text-decoration: none; border-radius: 5px; margin: 20px 0; }
                        .footer { background-color: #f5f5f5; padding: 10px; text-align: center; font-size: 12px; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>Special Offer!</h1>
                        </div>
                        <div class="content">
                            <h2>Hello {{recipient_name}},</h2>
                            <p>{{intro_text}}</p>
                            
                            <div class="offer">
                                <h2>{{offer_headline}}</h2>
                                <p>{{offer_details}}</p>
                                <p><strong>Use code: {{promo_code}}</strong></p>
                            </div>
                            
                            <p>{{offer_expiry_details}}</p>
                            <div style="text-align: center;">
                                <a href="{{cta_link}}" class="cta-button">{{cta_text}}</a>
                            </div>
                            
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
            )

        self.conn.commit()

    # Campaign management methods
    def add_campaign(self, name, subject=None, body_html=None, body_text=None, list_id=None, 
                    smtp_config_id=None, template_id=None):
        query = """
            INSERT INTO campaigns (
                name, subject, body_html, body_text, list_id, smtp_config_id, template_id, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return self.execute_query(
            query, 
            (name, subject, body_html, body_text, list_id, smtp_config_id, template_id, current_time), 
            commit=True
        )
    
    def update_campaign(self, campaign_id, **kwargs):
        # Build dynamic query based on provided fields
        set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        query = f"UPDATE campaigns SET {set_clause}, updated_at = ? WHERE id = ?"
        
        # Add current timestamp to parameters
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        params = list(kwargs.values())
        params.append(current_time)
        params.append(campaign_id)
        
        return self.execute_query(query, params, commit=True)
    
    def get_campaigns(self):
        return self.execute_query("SELECT * FROM campaigns ORDER BY updated_at DESC", fetch_all=True)
    
    def get_campaign_by_id(self, campaign_id):
        return self.execute_query("SELECT * FROM campaigns WHERE id = ?", (campaign_id,), fetch_one=True)
    
    def delete_campaign(self, campaign_id):
        return self.execute_query("DELETE FROM campaigns WHERE id = ?", (campaign_id,), commit=True)
    
    # Recipient list methods
    def add_recipient_list(self, name):
        query = "INSERT INTO recipient_lists (name) VALUES (?)"
        return self.execute_query(query, (name,), commit=True)
    
    def get_recipient_lists(self):
        return self.execute_query("SELECT * FROM recipient_lists ORDER BY created_at DESC", fetch_all=True)
    
    def get_recipient_list_by_id(self, list_id):
        return self.execute_query("SELECT * FROM recipient_lists WHERE id = ?", (list_id,), fetch_one=True)
    
    def delete_recipient_list(self, list_id):
        return self.execute_query("DELETE FROM recipient_lists WHERE id = ?", (list_id,), commit=True)
    
    # Recipient methods
    def add_recipient(self, list_id, email, name=None, domain=None, custom1=None, custom2=None, 
                     custom3=None, custom4=None, custom5=None):
        query = """
            INSERT INTO recipients (
                list_id, email, name, domain, custom1, custom2, custom3, custom4, custom5
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.execute_query(
            query, 
            (list_id, email, name, domain, custom1, custom2, custom3, custom4, custom5), 
            commit=True
        )
    
    def get_recipients_by_list(self, list_id):
        return self.execute_query("SELECT * FROM recipients WHERE list_id = ?", (list_id,), fetch_all=True)
    
    def get_recipient_by_id(self, recipient_id):
        return self.execute_query("SELECT * FROM recipients WHERE id = ?", (recipient_id,), fetch_one=True)
    
    def delete_recipient(self, recipient_id):
        return self.execute_query("DELETE FROM recipients WHERE id = ?", (recipient_id,), commit=True)
    
    def get_total_recipients(self):
        result = self.execute_query("SELECT COUNT(*) as count FROM recipients", fetch_one=True)
        return result['count'] if result else 0
    
    # SMTP configuration methods
    def add_smtp_config(self, profile_name, host, port, username, password, use_tls, sender_email, sender_name):
        query = """
            INSERT INTO smtp_configs (
                profile_name, host, port, username, password, use_tls, sender_email, sender_name
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.execute_query(
            query, 
            (profile_name, host, port, username, password, use_tls, sender_email, sender_name), 
            commit=True
        )
    
    def get_smtp_configs(self):
        return self.execute_query("SELECT * FROM smtp_configs", fetch_all=True)
    
    def get_smtp_config_by_id(self, config_id):
        return self.execute_query("SELECT * FROM smtp_configs WHERE id = ?", (config_id,), fetch_one=True)
    
    def update_smtp_config(self, config_id, **kwargs):
        # Build dynamic query based on provided fields
        set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        query = f"UPDATE smtp_configs SET {set_clause} WHERE id = ?"
        
        params = list(kwargs.values())
        params.append(config_id)
        
        return self.execute_query(query, params, commit=True)
    
    # Email template methods
    def add_email_template(self, name, subject, body_html):
        query = """
            INSERT INTO email_templates (name, subject, body_html)
            VALUES (?, ?, ?)
        """
        return self.execute_query(query, (name, subject, body_html), commit=True)
    
    def get_email_templates(self):
        return self.execute_query("SELECT * FROM email_templates ORDER BY created_at DESC", fetch_all=True)
    
    def get_email_template_by_id(self, template_id):
        return self.execute_query("SELECT * FROM email_templates WHERE id = ?", (template_id,), fetch_one=True)
    
    def update_email_template(self, template_id, **kwargs):
        # Build dynamic query based on provided fields
        set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        query = f"UPDATE email_templates SET {set_clause} WHERE id = ?"
        
        params = list(kwargs.values())
        params.append(template_id)
        
        return self.execute_query(query, params, commit=True)
    
    def delete_email_template(self, template_id):
        return self.execute_query("DELETE FROM email_templates WHERE id = ?", (template_id,), commit=True)
    
    # Email tracking methods
    def add_email_tracking(self, campaign_id, recipient_id, status, error_message=None):
        query = """
            INSERT INTO email_tracking (campaign_id, recipient_id, status, error_message)
            VALUES (?, ?, ?, ?)
        """
        return self.execute_query(query, (campaign_id, recipient_id, status, error_message), commit=True)
    
    def update_email_tracking(self, tracking_id, **kwargs):
        # Build dynamic query based on provided fields
        set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        query = f"UPDATE email_tracking SET {set_clause} WHERE id = ?"
        
        params = list(kwargs.values())
        params.append(tracking_id)
        
        return self.execute_query(query, params, commit=True)
    
    def get_email_tracking_by_campaign(self, campaign_id):
        query = """
            SELECT et.*, r.email, r.name
            FROM email_tracking et
            JOIN recipients r ON et.recipient_id = r.id
            WHERE et.campaign_id = ?
        """
        return self.execute_query(query, (campaign_id,), fetch_all=True)
    
    def get_campaign_stats(self, campaign_id):
        query = """
            SELECT 
                COUNT(*) as total_sent,
                SUM(CASE WHEN status = 'sent' THEN 1 ELSE 0 END) as delivered,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                SUM(CASE WHEN opened = 1 THEN 1 ELSE 0 END) as opened,
                SUM(CASE WHEN clicked = 1 THEN 1 ELSE 0 END) as clicked
            FROM email_tracking
            WHERE campaign_id = ?
        """
        return self.execute_query(query, (campaign_id,), fetch_one=True)
    
    # For analytics dashboard
    def get_all_campaign_stats(self):
        query = """
            SELECT 
                c.id,
                c.name,
                COUNT(et.id) as total_sent,
                SUM(CASE WHEN et.status = 'sent' THEN 1 ELSE 0 END) as delivered,
                SUM(CASE WHEN et.status = 'failed' THEN 1 ELSE 0 END) as failed,
                SUM(CASE WHEN et.opened = 1 THEN 1 ELSE 0 END) as opened,
                SUM(CASE WHEN et.clicked = 1 THEN 1 ELSE 0 END) as clicked
            FROM campaigns c
            LEFT JOIN email_tracking et ON c.id = et.campaign_id
            GROUP BY c.id
            ORDER BY COUNT(et.id) DESC
        """
        return self.execute_query(query, fetch_all=True)
