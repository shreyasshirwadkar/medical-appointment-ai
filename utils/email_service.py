import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import Dict, Any
import os
import config

class EmailService:
    """Email service for sending appointment confirmations and reminders."""
    
    def __init__(self):
        self.smtp_server = config.EMAIL_HOST
        self.smtp_port = config.EMAIL_PORT
        self.email_user = config.EMAIL_USER
        self.email_password = config.EMAIL_PASSWORD
    
    def send_confirmation_email(self, patient_data: Dict[str, Any], appointment_data: Dict[str, Any], insurance_data: Dict[str, Any]) -> bool:
        """Send appointment confirmation email with intake forms."""
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = patient_data.get('email', '')
            msg['Subject'] = f"Appointment Confirmation - {appointment_data['datetime'].strftime('%m/%d/%Y')}"
            
            # Email body
            body = self._create_confirmation_email_body(patient_data, appointment_data, insurance_data)
            msg.attach(MIMEText(body, 'html'))
            
            # Attach intake forms
            if os.path.exists(config.INTAKE_FORM_PDF):
                with open(config.INTAKE_FORM_PDF, "rb") as attachment:
                    part = MIMEApplication(attachment.read(), Name="Patient_Intake_Form.pdf")
                    part['Content-Disposition'] = 'attachment; filename="Patient_Intake_Form.pdf"'
                    msg.attach(part)
            
            # Send email
            if self.email_user and self.email_password:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
                server.quit()
                return True
            else:
                # Simulate email sending for demo
                print(f"Email would be sent to: {patient_data.get('email')}")
                print(f"Subject: {msg['Subject']}")
                return True
        
        except Exception as e:
            print(f"Error sending confirmation email: {e}")
            return False
    
    def send_reminder_email(self, to_email: str, subject: str, message: str, appointment_data: Dict[str, Any]) -> bool:
        """Send appointment reminder email."""
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Convert plain text message to HTML
            html_message = message.replace('\\n', '<br>')
            html_body = f"""
            <html>
            <head></head>
            <body>
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    {html_message}
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            if self.email_user and self.email_password:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
                server.quit()
                return True
            else:
                # Simulate email sending for demo
                print(f"Reminder email would be sent to: {to_email}")
                print(f"Subject: {subject}")
                return True
        
        except Exception as e:
            print(f"Error sending reminder email: {e}")
            return False
    
    def _create_confirmation_email_body(self, patient_data: Dict, appointment_data: Dict, insurance_data: Dict) -> str:
        """Create HTML email body for appointment confirmation."""
        
        appointment_date = appointment_data['datetime'].strftime('%A, %B %d, %Y')
        appointment_time = appointment_data['datetime'].strftime('%I:%M %p')
        
        html_body = f"""
        <html>
        <head>
            <style>
                .container {{ font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; }}
                .header {{ background-color: #2c5aa0; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .appointment-details {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .important {{ background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0; }}
                .footer {{ background-color: #6c757d; color: white; padding: 15px; text-align: center; font-size: 12px; }}
                ul {{ padding-left: 20px; }}
                li {{ margin: 5px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏥 Appointment Confirmed!</h1>
                </div>
                
                <div class="content">
                    <p>Dear {patient_data.get('name', 'Patient')},</p>
                    
                    <p>Your appointment has been successfully scheduled. Here are your details:</p>
                    
                    <div class="appointment-details">
                        <h3>📅 Appointment Details</h3>
                        <ul>
                            <li><strong>Date:</strong> {appointment_date}</li>
                            <li><strong>Time:</strong> {appointment_time}</li>
                            <li><strong>Doctor:</strong> Dr. {appointment_data.get('doctor', '')}</li>
                            <li><strong>Duration:</strong> {appointment_data.get('duration', 60)} minutes</li>
                            <li><strong>Location:</strong> {appointment_data.get('location', '')}</li>
                            <li><strong>Appointment ID:</strong> {appointment_data.get('appointment_id', '')}</li>
                        </ul>
                    </div>
                    
                    <div class="appointment-details">
                        <h3>🏥 Insurance Information</h3>
                        <ul>
                            <li><strong>Carrier:</strong> {insurance_data.get('insurance_carrier', '')}</li>
                            <li><strong>Member ID:</strong> {insurance_data.get('member_id', '')}</li>
                            <li><strong>Group Number:</strong> {insurance_data.get('group_number', 'N/A')}</li>
                        </ul>
                    </div>
                    
                    <div class="important">
                        <h3>📋 Important Reminders</h3>
                        <ul>
                            <li>Please arrive 15 minutes early for check-in</li>
                            <li>Bring a valid photo ID</li>
                            <li>Bring your insurance card</li>
                            <li>Complete the attached intake forms before your visit</li>
                            <li>Bring a list of current medications</li>
                        </ul>
                    </div>
                    
                    <p><strong>📎 Attached Documents:</strong></p>
                    <ul>
                        <li>Patient Intake Form - Please complete and bring with you</li>
                    </ul>
                    
                    <p><strong>📞 Need to make changes?</strong><br>
                    Contact us at least 24 hours in advance to reschedule or cancel your appointment.</p>
                    
                    <p>We look forward to seeing you!</p>
                    
                    <p>Best regards,<br>
                    The Medical Scheduling Team</p>
                </div>
                
                <div class="footer">
                    <p>This is an automated message. Please do not reply to this email.</p>
                    <p>© 2025 AI Medical Scheduling System</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_body
    
    def send_form_completion_reminder(self, patient_email: str, patient_name: str, appointment_date: str) -> bool:
        """Send reminder to complete intake forms."""
        
        subject = f"Action Required: Complete Your Intake Forms - Appointment {appointment_date}"
        
        html_body = f"""
        <html>
        <head></head>
        <body style="font-family: Arial, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto;">
                <h2>📋 Intake Forms Reminder</h2>
                <p>Dear {patient_name},</p>
                <p>We hope you're looking forward to your upcoming appointment on <strong>{appointment_date}</strong>.</p>
                <p>To help us provide you with the best care possible, please remember to complete your intake forms before your visit.</p>
                <p>If you haven't received the forms or need assistance, please contact us immediately.</p>
                <p>Thank you for your attention to this matter.</p>
                <p>Best regards,<br>The Medical Team</p>
            </div>
        </body>
        </html>
        """
        
        return self.send_reminder_email(patient_email, subject, html_body, {})
