import re
import smtplib
import socket
import dns.resolver
import time
import random


# Class to validate the existence of an email address
class EmailExistenceValidator:
    def __init__(self):
        # Default status dictionary
        self.status = {
            "isValid": False,  # Flag indicating whether the email is valid
            "response_status": "",  # Description of the validation status
            "response_code": 221,  # Default SMTP response code
            "smtp_server_message": "None",  # Message from the SMTP server
            "color_code": "red",  # Default color for status
        }
        # Initialize last validation time to handle rate limiting
        self.last_validation_time = 0

    # Method to validate an email address
    def validate_email(self, email):
        """
        Validates the given email address.

        Args:
            email (str): The email address to be validated.

        Returns:
            dict: A dictionary containing the validation results.
        """
        # Limit validation frequency to avoid rate limiting
        current_time = time.time()
        if current_time - self.last_validation_time < 5:
            time.sleep(random.uniform(0.1, 0.5))  # Introduce random delay
        self.last_validation_time = current_time

        # Check email format using regular expression
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            self.status["response_status"] = "Invalid email format"
            return self.status

        # Extract domain and perform MX lookup to get mail server addresses
        domain = email.split("@")[-1]
        try:
            mx_records = dns.resolver.resolve(domain, "MX")
        except (
            dns.resolver.NoAnswer,
            dns.resolver.NXDOMAIN,
            dns.resolver.Timeout,
        ) as e:
            # Handle DNS resolution errors
            self.status["response_status"] = str(e)
            return self.status

        # Try SMTP verification for each mail server found
        for mx in mx_records:
            mx_host = str(mx.exchange)[:-1]  # Extract the mail server hostname
            try:
                with smtplib.SMTP(mx_host, timeout=10) as smtp:
                    smtp.ehlo_or_helo_if_needed()

                    # Verify the email address with SMTP server
                    status_code, message = smtp.verify(email)
                    if status_code in {250, 251, 252}:
                        self.status["isValid"] = True
                        self.status["response_status"] = "Email is valid"
                        self.status["color_code"] = (
                            "green"  # Valid email, set color to green
                        )
                    elif status_code == 550:
                        self.status["response_status"] = "Recipient address rejected"
                        self.status["color_code"] = (
                            "yellow"  # Rejected email, set color to yellow
                        )
                    else:
                        self.status["response_status"] = (
                            f"Unexpected SMTP response: {status_code}"
                        )
                        self.status["color_code"] = (
                            "red"  # Unexpected response, set color to red
                        )
                    self.status["smtp_server_message"] = message
            except (
                smtplib.SMTPServerDisconnected,
                smtplib.SMTPConnectError,
                smtplib.SMTPNotSupportedError,
                smtplib.SMTPResponseException,
                smtplib.SMTPException,
            ) as e:
                # Handle SMTP connection errors
                self.status["response_status"] = str(e)
                self.status["color_code"] = "red"  # Connection error, set color to red
                # return self.status

        # Check for address existence using email address enumeration
        try:
            with smtplib.SMTP(mx_host, timeout=10) as smtp:
                local_ip_address = socket.gethostbyname(socket.gethostname())
                source_address = (local_ip_address, 0)
                smtp.connect(host=mx_host, port=25, source_address=source_address)
                smtp.ehlo_or_helo_if_needed()
                status_code, message = smtp.mail("")
                smtp.rcpt(email)
                msg = "\r\n".join(
                    [
                        "From: user.me@example.com",
                        "To: user.you@example.com",
                        "Subject: Just a message",
                        "",
                        "Why, oh why, would you want to do a thing like that?",
                        "",
                    ]
                )

                # Send a test message to verify recipient address
                smtp.data(msg)
                self.status["response_code"] = status_code
                self.status["smtp_server_message"] = message
                if status_code in {250, 251, 252}:
                    self.status["isValid"] = True
                    self.status["response_status"] = "Email is valid"
                    self.status["color_code"] = (
                        "green"  # Valid email, set color to green
                    )
                elif status_code == 550:
                    self.status["response_status"] = "Recipient address rejected"
                    self.status["color_code"] = (
                        "yellow"  # Rejected email, set color to yellow
                    )
                else:
                    self.status["response_status"] = "Recipient address does not exist"
                    self.status["color_code"] = (
                        "red"  # Non-existent address, set color to red
                    )
        except smtplib.SMTPException as e:
            # Handle SMTP errors
            if hasattr(e, "smtp_error"):
                self.status["response_status"] = e.smtp_error.decode()
            else:
                self.status["response_status"] = str(e)
            match = re.search(r"\b\d+\b", str(e))
            self.status["response_code"] = int(match.group()) if match else None
            if (
                self.status["response_code"] is not None
                and 500 <= self.status["response_code"] <= 599
                or self.status["response_code"] is None
            ):
                self.status["isValid"] = False
                self.status["color_code"] = "red"  # Permanent failure, set color to red

        # Store the email being tested and return the validation status
        self.status["email_tested"] = email
        return self.status


# Example usage

# email = "mogecot375@darkse.com"
# validator = EmailExistenceValidator()
# result = validator.validate_email(email)
# print(result)
