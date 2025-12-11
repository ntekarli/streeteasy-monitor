import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .utils import get_datetime


class EmailNotifier:
    def __init__(self, smtp_config):
        self.smtp_server = smtp_config['server']
        self.smtp_port = smtp_config['port']
        self.sender_email = smtp_config['username']
        self.sender_password = smtp_config['password']
        self.recipient_email = smtp_config['recipient']

    def send_listing_notification(self, listing):
        """Send email notification for a new listing."""
        subject = f"New Listing: {listing['address']} - ${listing['price']}"
        body = self._format_email_body(listing)
        
        try:
            self._send_email(subject, body)
            print(f'{get_datetime()} Email sent successfully to {self.recipient_email}\n')
            return True
        except Exception as e:
            print(f'{get_datetime()} Error sending email: {e}\n')
            return False

    def _format_email_body(self, listing):
        """Format listing details for email."""
        return f"""
New rental listing found!

Address: {listing['address']}
Price: ${listing['price']}
Neighborhood: {listing['neighborhood']}
Listing URL: {listing['url']}

---
StreetEasy Monitor
"""

    def _send_email(self, subject, body):
        """Send email via SMTP."""
        message = MIMEMultipart()
        message['From'] = self.sender_email
        message['To'] = self.recipient_email
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(message)
