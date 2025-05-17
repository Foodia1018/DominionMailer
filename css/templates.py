"""
Email template gallery for DominionMailer
This module provides a collection of pre-designed email templates with descriptions
and preview images.
"""

def get_templates():
    """
    Returns a list of available email templates with preview images
    
    Each template has:
    - name: Display name of the template
    - description: Short description of what the template is for
    - image_url: URL to a preview image
    - subject: Default subject line
    - html: HTML content of the template
    
    Returns:
        list: A list of template dictionaries
    """
    templates = [
        {
            "name": "Modern Newsletter",
            "description": "Professional newsletter template with sections for multiple articles and updates.",
            "image_url": "https://pixabay.com/get/g89bc7c096193576b44cd5330b621f5869460916fc2088457499c08f98394170d2ab25f83f9aa9afbff01787dcf50c5d1d57ecf79a31223f5aa1ded3c2939830b_1280.jpg",
            "subject": "{{company_name}} Newsletter - {{newsletter_date}}",
            "html": """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; margin: 0; padding: 0; }
                    .container { width: 100%; max-width: 600px; margin: 0 auto; }
                    .header { background-color: #5E81AC; color: white; padding: 20px; text-align: center; }
                    .content { padding: 20px; }
                    .article { margin-bottom: 25px; border-bottom: 1px solid #eee; padding-bottom: 15px; }
                    .article h2 { color: #4C566A; margin-top: 0; }
                    .article img { max-width: 100%; height: auto; }
                    .cta-button { display: inline-block; background-color: #5E81AC; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; }
                    .footer { background-color: #3B4252; color: #D8DEE9; padding: 15px; text-align: center; font-size: 12px; }
                    .social-links { margin: 10px 0; }
                    .social-links a { color: #88C0D0; margin: 0 5px; text-decoration: none; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>{{company_name}} Newsletter</h1>
                        <p>{{newsletter_date}}</p>
                    </div>
                    <div class="content">
                        <p>Hello {{recipient_name}},</p>
                        <p>{{greeting_text}}</p>
                        
                        <div class="article">
                            <h2>{{article1_title}}</h2>
                            <p>{{article1_content}}</p>
                            <a href="#" class="cta-button">Read More</a>
                        </div>
                        
                        <div class="article">
                            <h2>{{article2_title}}</h2>
                            <p>{{article2_content}}</p>
                            <a href="#" class="cta-button">Learn More</a>
                        </div>
                        
                        <div class="article">
                            <h2>Upcoming Events</h2>
                            <p>Stay tuned for our upcoming events and webinars.</p>
                        </div>
                        
                        <p>Thank you for your continued support!</p>
                        <p>Best regards,<br>{{sender_name}}</p>
                    </div>
                    <div class="footer">
                        <div class="social-links">
                            <a href="#">Twitter</a> | <a href="#">Facebook</a> | <a href="#">LinkedIn</a>
                        </div>
                        <p>© {{current_year}} {{company_name}}. All rights reserved.</p>
                        <p><a href="{{unsubscribe_link}}" style="color: #88C0D0;">Unsubscribe</a> | <a href="{{view_in_browser_link}}" style="color: #88C0D0;">View in browser</a></p>
                    </div>
                </div>
            </body>
            </html>
            """
        },
        {
            "name": "Special Offer",
            "description": "Eye-catching promotional template for special offers and discounts.",
            "image_url": "https://pixabay.com/get/g999610b311d6ede7c743fccd919fdd2b4dbd4a13429fed08578c7a6310082a076d82fddb5477d03dbb07c05f6075ae8549b9225dee7e2cbda430a7211ef98289_1280.jpg",
            "subject": "Special Offer Inside! Limited Time Only",
            "html": """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; margin: 0; padding: 0; }
                    .container { width: 100%; max-width: 600px; margin: 0 auto; }
                    .header { background-color: #A3BE8C; color: white; padding: 20px; text-align: center; }
                    .content { padding: 20px; }
                    .offer { background-color: #EBCB8B; padding: 15px; text-align: center; margin: 20px 0; border-radius: 5px; }
                    .offer h2 { color: #2E3440; margin-top: 0; }
                    .discount { font-size: 36px; font-weight: bold; color: #BF616A; margin: 10px 0; }
                    .cta-button { display: inline-block; background-color: #5E81AC; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; font-weight: bold; font-size: 16px; }
                    .footer { background-color: #3B4252; color: #D8DEE9; padding: 15px; text-align: center; font-size: 12px; }
                    .expiry { background-color: #f0f0f0; padding: 10px; text-align: center; font-weight: bold; color: #2E3440; margin-top: 20px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Special Offer Just For You!</h1>
                    </div>
                    <div class="content">
                        <p>Hello {{recipient_name}},</p>
                        <p>{{intro_text}}</p>
                        
                        <div class="offer">
                            <h2>{{offer_headline}}</h2>
                            <div class="discount">{{promo_code}}</div>
                            <p>{{offer_details}}</p>
                        </div>
                        
                        <div style="text-align: center;">
                            <a href="{{cta_link}}" class="cta-button">{{cta_text}}</a>
                        </div>
                        
                        <div class="expiry">
                            {{offer_expiry_details}}
                        </div>
                        
                        <p>Best regards,<br>{{sender_name}}</p>
                    </div>
                    <div class="footer">
                        <p>© {{current_year}} {{company_name}}. All rights reserved.</p>
                        <p><a href="{{unsubscribe_link}}" style="color: #88C0D0;">Unsubscribe</a> | <a href="{{view_in_browser_link}}" style="color: #88C0D0;">View in browser</a></p>
                        <p>If you have any questions, please contact our support team.</p>
                    </div>
                </div>
            </body>
            </html>
            """
        },
        {
            "name": "Minimalist Announcement",
            "description": "Clean, simple template for company announcements and updates.",
            "image_url": "https://pixabay.com/get/gdf5d6d0a01a957a27aa412e4d7c1ee22726f242a37768d11462a80ef968250b5c2d6731966d495e98b09b2f47afb1f6340b4a51a186e59b771ec040bdf105957_1280.jpg",
            "subject": "Important Announcement from {{company_name}}",
            "html": """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f9f9f9; }
                    .container { width: 100%; max-width: 600px; margin: 0 auto; background-color: #ffffff; }
                    .header { border-bottom: 3px solid #5E81AC; padding: 20px; text-align: center; }
                    .logo { font-size: 24px; font-weight: bold; color: #5E81AC; }
                    .content { padding: 30px 20px; line-height: 1.6; color: #333; }
                    .signature { margin-top: 30px; border-top: 1px solid #eeeeee; padding-top: 20px; }
                    .footer { background-color: #f5f5f5; padding: 15px; text-align: center; font-size: 12px; color: #666; }
                    .announcement-title { font-size: 22px; color: #2E3440; margin-bottom: 20px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="logo">{{company_name}}</div>
                    </div>
                    <div class="content">
                        <p>Hello {{recipient_name}},</p>
                        
                        <div class="announcement-title">{{article1_title}}</div>
                        
                        <p>{{article1_content}}</p>
                        
                        <p>If you have any questions or would like to learn more, please don't hesitate to reach out.</p>
                        
                        <div class="signature">
                            <p>Best regards,<br>
                            {{sender_name}}<br>
                            {{company_name}}</p>
                        </div>
                    </div>
                    <div class="footer">
                        <p>© {{current_year}} {{company_name}}. All rights reserved.</p>
                        <p><a href="{{unsubscribe_link}}" style="color: #5E81AC;">Unsubscribe</a> | <a href="{{view_in_browser_link}}" style="color: #5E81AC;">View in browser</a></p>
                    </div>
                </div>
            </body>
            </html>
            """
        },
        {
            "name": "Analytics Report",
            "description": "Data-focused template for sending reports and analytics summaries.",
            "image_url": "https://pixabay.com/get/g138a0b5b3cdae7fa948ec334272b9e592e9329f30c58d0e9809a81bdd18489c108e729c9d72b86d45555064a5ea312be63e8a341530b5e8e64facc25949a2c94_1280.jpg",
            "subject": "Your {{company_name}} Analytics Report",
            "html": """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; margin: 0; padding: 0; }
                    .container { width: 100%; max-width: 600px; margin: 0 auto; }
                    .header { background-color: #4C566A; color: white; padding: 20px; text-align: center; }
                    .content { padding: 20px; }
                    .metric-row { display: flex; margin-bottom: 20px; }
                    .metric { flex: 1; text-align: center; padding: 15px; background-color: #f0f0f0; margin: 0 5px; border-radius: 5px; }
                    .metric-value { font-size: 28px; font-weight: bold; color: #5E81AC; margin: 10px 0; }
                    .metric-label { font-size: 14px; color: #4C566A; }
                    .chart-placeholder { background-color: #f0f0f0; height: 200px; display: flex; align-items: center; justify-content: center; margin: 20px 0; border-radius: 5px; }
                    .section { margin-bottom: 30px; }
                    .section-title { font-size: 18px; color: #4C566A; margin-bottom: 15px; padding-bottom: 5px; border-bottom: 1px solid #eee; }
                    .footer { background-color: #3B4252; color: #D8DEE9; padding: 15px; text-align: center; font-size: 12px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Analytics Report</h1>
                        <p>{{newsletter_date}}</p>
                    </div>
                    <div class="content">
                        <p>Hello {{recipient_name}},</p>
                        <p>Here's your latest analytics report from {{company_name}}.</p>
                        
                        <div class="section">
                            <div class="section-title">Key Metrics</div>
                            <div class="metric-row">
                                <div class="metric">
                                    <div class="metric-label">Total Visitors</div>
                                    <div class="metric-value">1,245</div>
                                </div>
                                <div class="metric">
                                    <div class="metric-label">Conversion Rate</div>
                                    <div class="metric-value">5.2%</div>
                                </div>
                                <div class="metric">
                                    <div class="metric-label">Avg. Time</div>
                                    <div class="metric-value">3:24</div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="section">
                            <div class="section-title">Performance Overview</div>
                            <p>{{article1_content}}</p>
                            <div class="chart-placeholder">Chart: Monthly Performance</div>
                        </div>
                        
                        <div class="section">
                            <div class="section-title">Recommendations</div>
                            <p>{{article2_content}}</p>
                        </div>
                        
                        <p>For a detailed breakdown, please log into your dashboard.</p>
                        <p>Best regards,<br>{{sender_name}}</p>
                    </div>
                    <div class="footer">
                        <p>© {{current_year}} {{company_name}}. All rights reserved.</p>
                        <p><a href="{{unsubscribe_link}}" style="color: #88C0D0;">Unsubscribe</a> | <a href="{{view_in_browser_link}}" style="color: #88C0D0;">View in browser</a></p>
                    </div>
                </div>
            </body>
            </html>
            """
        }
    ]
    
    return templates
