import re
import smtplib
import socket
import dns.resolver
import time
import random

"""
The `EmailExistenceValidator` class performs an enumeration check to determine the validity of an email address. This process involves simulating the interaction with the SMTP server associated with the recipient's domain. Here's how it works:

1. Establish a connection to the SMTP server associated with one of the mail servers obtained from the MX lookup.
2. Initiate the SMTP session with an EHLO command.
3. Send a MAIL FROM command with an empty sender address.
4. Send a RCPT TO command with the target email address.

The SMTP server's response to the RCPT TO command is used to determine the validity of the email address:

- A status code of 250, 251, or 252 indicates that the email address is valid or deliverable.
- A status code of 550 signifies that the recipient address is rejected.
- Any other status code suggests that the recipient address does not exist.

The `status` dictionary is then updated with the response code and message. Additionally, any SMTP exceptions encountered during the process are handled, and the email validity status is adjusted accordingly based on the response code, with permanent failures (500-599) marking the email as invalid.
"""


class EmailExistenceValidator:
    def __init__(self):
        """
        Initializes the EmailExistenceValidator object with default values.
        """
        self.status = {
            "isValid": False,  # Flag indicating whether the email is valid
            "response_status": "",  # Description of the validation status
            "response_code": 200,  # SMTP response code (default: 200 OK)
            "smtp_server_message": "None",  # Message from the SMTP server
        }
        # Initialize last validation time to handle rate limiting
        self.last_validation_time = 0

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
        if (
            current_time - self.last_validation_time < 5
        ):  # Adjust time interval as needed
            time.sleep(random.uniform(0.1, 0.5))  # Introduce random delay
        self.last_validation_time = current_time

        # Check email format using regular expression
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            self.status["response_status"] = "Invalid email format"
            return self.status

        # Extract domain and perform MX lookup to get mail server addresses
        domain = email.split("@")[-1]
        try:
            mx_records = dns.resolver.resolve(
                domain, "MX"
            )  # Resolve MX records for the domain
        except (
            dns.resolver.NoAnswer,
            dns.resolver.NXDOMAIN,
            dns.resolver.Timeout,
        ) as e:
            self.status["response_status"] = str(e)
            return self.status

        # Try SMTP verification for each mail server found
        for mx in mx_records:
            mx_host = str(mx.exchange)[:-1]  # Extract the mail server hostname
            try:
                with smtplib.SMTP(mx_host, timeout=10) as smtp:
                    smtp.ehlo()
                    status_code, message = smtp.verify(
                        email
                    )  # Verify the email address
                    self.status["response_code"] = status_code
                    if status_code in {250, 251, 252}:
                        self.status["isValid"] = True
                        self.status["response_status"] = "Email is valid"
                    elif status_code == 550:
                        self.status["response_status"] = "Recipient address rejected"
                    else:
                        self.status["response_status"] = (
                            f"Unexpected SMTP response: {status_code}"
                        )
                    self.status["smtp_server_message"] = message
            except (
                smtplib.SMTPServerDisconnected,
                smtplib.SMTPConnectError,
                smtplib.SMTPNotSupportedError,
                smtplib.SMTPResponseException,
                smtplib.SMTPException,
            ) as e:
                self.status["response_status"] = str(e)
                return self.status

        # Check for address existence using email address enumeration

        try:
            with smtplib.SMTP(mx_host, timeout=10) as smtp:
                local_ip_address = socket.gethostbyname(socket.gethostname())
                source_address = (local_ip_address, 0)
                smtp.connect(host=mx_host, port=25, source_address=source_address)
                smtp.ehlo()
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

                smtp.data(msg)
                self.status["response_code"] = status_code
                self.status["smtp_server_message"] = message
                if status_code in {250, 251, 252}:
                    self.status["isValid"] = True
                    self.status["response_status"] = "Email is valid"
                elif status_code == 550:
                    self.status["response_status"] = "Recipient address rejected"
                else:
                    self.status["response_status"] = "Recipient address does not exist"

        except smtplib.SMTPException as e:
            if hasattr(e, "smtp_error"):
                self.status["response_status"] = e.smtp_error.decode()
            else:
                self.status["response_status"] = str(e)
            match = re.search(r"\b\d+\b", str(e))
            self.status["response_code"] = int(match.group()) if match else None
            if (
                self.status["response_code"] is not None
                and 500 <= self.status["response_code"] <= 599
            ):
                self.status["isValid"] = False

        # Store the email being tested and return the validation status
        self.status["email_tested"] = email
        return self.status


# Example usage
email = "mogecot375@darkse.com"
validator = EmailExistenceValidator()
result = validator.validate_email(email)
print(result)
