import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.mailtrap.io')
        self.smtp_port = int(os.getenv('SMTP_PORT', '2525'))
        self.smtp_user = os.getenv('SMTP_USER', 'dummy')
        self.smtp_pass = os.getenv('SMTP_PASS', 'dummy')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@eshop.com')
        self.from_name = os.getenv('FROM_NAME', 'E-Shop')

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        cc: Optional[str] = None,
        bcc: Optional[str] = None
    ) -> bool:
        """
        Send email using SMTP
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Plain text email body
            html_body: Optional HTML email body
            cc: Optional CC recipient
            bcc: Optional BCC recipient
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = f"{self.from_name} <{self.from_email}>"
            message['To'] = to_email
            
            if cc:
                message['Cc'] = cc
            if bcc:
                message['Bcc'] = bcc
            
            # Add plain text part
            text_part = MIMEText(body, 'plain')
            message.attach(text_part)
            
            # Add HTML part if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                message.attach(html_part)
            
            # Connect to SMTP server and send
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_user and self.smtp_pass:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_pass)
                
                # Prepare recipients list
                recipients = [to_email]
                if cc:
                    recipients.extend(cc.split(','))
                if bcc:
                    recipients.extend(bcc.split(','))
                
                server.send_message(message, to_addrs=recipients)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    def generate_order_confirmation_html(self, order_data: dict) -> str:
        """Generate HTML email for order confirmation"""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Order Confirmation</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: #3b82f6; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background: #f9fafb; }
                .order-details { background: white; padding: 15px; border-radius: 5px; margin: 20px 0; }
                .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
                .button { display: inline-block; background: #3b82f6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Order Confirmation</h1>
                    <p>Thank you for your purchase!</p>
                </div>
                
                <div class="content">
                    <p>Dear Customer,</p>
                    <p>We're pleased to confirm that we've received your order. Here are the details:</p>
                    
                    <div class="order-details">
                        <h2>Order Details</h2>
                        <p><strong>Order ID:</strong> {order_id}</p>
                        <p><strong>Date:</strong> {date}</p>
                        <p><strong>Total Amount:</strong> ${total_amount}</p>
                        <p><strong>Status:</strong> {status}</p>
                    </div>
                    
                    <p>We'll send you another email when your order ships.</p>
                    
                    <a href="#" class="button">Track Your Order</a>
                    
                    <p>If you have any questions, please don't hesitate to contact our customer service.</p>
                </div>
                
                <div class="footer">
                    <p>&copy; 2024 E-Shop. All rights reserved.</p>
                    <p>This is an automated message. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_template.format(
            order_id=order_data.get('order_id'),
            date=datetime.now().strftime('%B %d, %Y'),
            total_amount=order_data.get('total_amount'),
            status=order_data.get('status', 'pending')
        )

    def generate_welcome_html(self, user_data: dict) -> str:
        """Generate HTML email for welcome message"""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome to E-Shop</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: #10b981; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background: #f9fafb; }
                .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
                .button { display: inline-block; background: #10b981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to E-Shop!</h1>
                    <p>We're excited to have you join our community</p>
                </div>
                
                <div class="content">
                    <p>Dear {user_email},</p>
                    <p>Thank you for registering with E-Shop! Your account has been successfully created.</p>
                    
                    <h2>What's Next?</h2>
                    <ul>
                        <li>Browse our extensive product catalog</li>
                        <li>Create your wishlist</li>
                        <li>Enjoy exclusive member benefits</li>
                        <li>Get notified about special deals</li>
                    </ul>
                    
                    <a href="#" class="button">Start Shopping</a>
                    
                    <p>If you have any questions or need assistance, our customer service team is here to help.</p>
                </div>
                
                <div class="footer">
                    <p>&copy; 2024 E-Shop. All rights reserved.</p>
                    <p>This is an automated message. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_template.format(
            user_email=user_data.get('email', 'Customer')
        )
