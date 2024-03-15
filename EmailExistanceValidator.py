import re
import smtplib
import socket
import dns.resolver
import time
import random


class EmailExistanceValidator:
    def __init__(self):
        self.status = {
            "isValid": False,
            "response_status": "",
            "response_code": 200,
            "smtp_server_message": "None",
        }
        self.last_validation_time = 0

    def validate_email(self, email):
        # Limit validation frequency to avoid rate limiting
        current_time = time.time()
        if (
            current_time - self.last_validation_time < 5
        ):  # Adjust time interval as needed
            time.sleep(random.uniform(0.1, 0.5))  # Introduce random delay
        self.last_validation_time = current_time

        # Check email format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            self.status["response_status"] = "Invalid email format"
            return self.status

        # Extract domain and perform MX lookup
        domain = email.split("@")[-1]
        try:
            mx_records = dns.resolver.resolve(domain, "MX")
        except (
            dns.resolver.NoAnswer,
            dns.resolver.NXDOMAIN,
            dns.resolver.Timeout,
        ) as e:
            self.status["response_status"] = str(e)
            return self.status

        # Try SMTP verification
        for mx in mx_records:
            mx_host = str(mx.exchange)[:-1]
            try:
                with smtplib.SMTP(mx_host, timeout=10) as smtp:
                    smtp.ehlo()
                    status_code, message = smtp.verify(email)
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

        # Additional check for email address existence using email address enumeration
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
            if 500 <= self.status["response_code"] <= 599:
                self.status["isValid"] = False
        self.status["email_tested"] = email
        return self.status


# Example usage
email = "salmantariquuuu8385@gmail.com"
validator = EmailExistanceValidator()
result = validator.validate_email(email)
print(result)
