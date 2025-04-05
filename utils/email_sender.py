import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
from config import EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASSWORD, CONTACT_EMAIL


class EmailSender:
    """Class for sending emails"""

    def __init__(self):
        self.host = EMAIL_HOST
        self.port = EMAIL_PORT
        self.username = EMAIL_USER
        self.password = EMAIL_PASSWORD
        self.contact_email = CONTACT_EMAIL

    def validate_email(self, email):
        """Validate that the email is in a correct format"""
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None

    def validate_form(self, name, email, subject, message):
        """Validate the contact form"""
        errors = []

        if not name.strip():
            errors.append("Name is required.")

        if not email.strip():
            errors.append("Email is required.")
        elif not self.validate_email(email):
            errors.append("Please enter a valid email address.")

        if not subject.strip():
            errors.append("Subject is required.")

        if not message.strip():
            errors.append("Message is required.")
        elif len(message) < 10:
            errors.append("Message is too short. Please provide more details.")

        return errors

    def send_contact_email(self, name, email, subject, message, recipient="mohdzohakhan@gmail.com"):
        """Send a contact email to a specific recipient"""
   #     if not self.username or not self.password:
   #         raise ValueError("Email credentials are not configured.")

        # If recipient is not provided, default to self.contact_email
        # Create a multipart message
        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = recipient
        msg['Subject'] = f"Contact Form: {subject}"

        # Create the email body
        body = f"""
        New contact form submission:

        Name: {name}
        Email: {email}
        Subject: {subject}

        Message:
        {message}
        """

        # Attach the body to the email
        msg.attach(MIMEText(body, 'plain'))

        try:
            # Connect to the SMTP server
            server = smtplib.SMTP(self.host, self.port)
            server.ehlo()
            server.starttls()
            server.ehlo()

            # Login to the SMTP server
            server.login(self.username, self.password)

            # Send the email
            server.sendmail(self.username, recipient, msg.as_string())

            # Close the connection
            server.close()

            return True, "Your message has been sent successfully! We'll get back to you soon."
        except Exception as e:
            return False, f"Failed to send email: {str(e)}"

    def send_notification_email(self, to_email, subject, message):
        """Send a notification email"""
       # if not self.username or not self.password:
        #    raise ValueError("Email credentials are not configured.")

        # Create a multipart message
        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = to_email
        msg['Subject'] = subject

        # Attach the body to the email
        msg.attach(MIMEText(message, 'plain'))

        try:
            # Connect to the SMTP server
            server = smtplib.SMTP(self.host, self.port)
            server.ehlo()
            server.starttls()
            server.ehlo()

            # Login to the SMTP server
            server.login(self.username, self.password)

            # Send the email
            server.sendmail(self.username, to_email, msg.as_string())

            # Close the connection
            server.close()

            return True, "Notification email sent successfully."
        except Exception as e:
            return False, f"Failed to send notification email: {str(e)}"

