import re
import smtplib
import socket
import dns.resolver
import time
import random
import requests


class EmailExistenceValidator:
    def __init__(self):
        self.status = {
            "isValid": False,
            "response_status": "",
            "response_code": None,
            "smtp_server_message": "None",
            "color_code": "red",
        }
        self.spam_trap_domains = set(["spamtrap.com", "spammer.net"])
        self.toxic_domains = set(["toxicsite.com", "malicious.net"])
        self.disposable_email_domains = self.load_disposable_domains()
        self.bounced_emails = set()
        self.valid_emails = set()
        self.unsure_emails = set()
        self.undeliverable_emails = set()
        self.last_validation_time = 0
        self.gdpr_compliant = False

    def load_disposable_domains(self):
        url = "https://raw.githubusercontent.com/disposable-email-domains/disposable-email-domains/master/disposable_email_blacklist.conf"
        response = requests.get(url)
        return set(response.text.splitlines())

    def deduplicate(self, email_list):
        deduplicated_list = list(set(email_list))
        self.valid_emails.update(deduplicated_list)
        return deduplicated_list

    def is_spam_trap(self, domain):
        return domain in self.spam_trap_domains

    def is_toxic_domain(self, domain):
        return domain in self.toxic_domains

    def is_disposable_email(self, domain):
        return domain in self.disposable_email_domains

    def validate_mta(self, mx_record):
        try:
            socket.gethostbyname(mx_record)
            return True
        except socket.error:
            return False

    def categorize_email(self, email):
        if self.status["isValid"]:
            self.valid_emails.add(email)
        elif "Bounce detected" in self.status["response_status"]:
            self.bounced_emails.add(email)
        elif "Unexpected SMTP response" in self.status["response_status"]:
            self.unsure_emails.add(email)
        else:
            self.undeliverable_emails.add(email)

    def validate_email(self, email):
        if not self.gdpr_compliant:
            self.status["response_status"] = "GDPR compliance not ensured"
            self.status["color_code"] = "red"
            self.categorize_email(email)
            return self.status

        if email in self.valid_emails:
            self.status["response_status"] = "Duplicate email detected"
            return self.status

        current_time = time.time()
        if current_time - self.last_validation_time < 5:
            time.sleep(random.uniform(0.1, 0.5))
        self.last_validation_time = current_time

        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            self.status["response_status"] = "Invalid email format"
            self.status["color_code"] = "red"
            self.categorize_email(email)
            return self.status

        domain = email.split("@")[-1]

        if self.is_spam_trap(domain):
            self.status["response_status"] = "Spam trap domain detected"
            self.status["color_code"] = "yellow"
            self.categorize_email(email)
            return self.status

        if self.is_toxic_domain(domain):
            self.status["response_status"] = "Toxic domain detected"
            self.status["color_code"] = "yellow"
            self.categorize_email(email)
            return self.status

        if self.is_disposable_email(domain):
            self.status["response_status"] = "Disposable email address detected"
            self.status["color_code"] = "yellow"
            self.categorize_email(email)
            return self.status

        try:
            mx_records = dns.resolver.resolve(domain, "MX")
        except (
            dns.resolver.NoAnswer,
            dns.resolver.NXDOMAIN,
            dns.resolver.Timeout,
        ) as e:
            self.status["response_status"] = str(e)
            self.status["color_code"] = "red"
            self.categorize_email(email)
            return self.status

        for mx in mx_records:
            mx_host = str(mx.exchange).rstrip(".")

            if not self.validate_mta(mx_host):
                self.status["response_status"] = "Invalid MTA detected"
                self.status["color_code"] = "red"
                self.categorize_email(email)
                return self.status

            try:
                with smtplib.SMTP(mx_host, timeout=10) as smtp:
                    smtp.ehlo_or_helo_if_needed()

                    sender_email = "no-reply@yourdomain.com"
                    smtp.mail(sender_email)
                    status_code, message = smtp.rcpt(email)

                    self.status["smtp_server_message"] = message.decode("utf-8")
                    self.status["response_code"] = status_code

                    if status_code == 250:
                        self.status["isValid"] = True
                        self.status["response_status"] = "Email is valid"
                        self.status["color_code"] = "green"
                        self.categorize_email(email)
                        return self.status
                    elif status_code == 550:
                        self.status["response_status"] = (
                            "Recipient address rejected (Bounce detected)"
                        )
                        self.status["color_code"] = "yellow"
                        self.categorize_email(email)
                        return self.status
                    else:
                        self.status["response_status"] = (
                            f"Unexpected SMTP response: {status_code}"
                        )
                        self.status["color_code"] = "red"
                        self.categorize_email(email)
            except (
                smtplib.SMTPServerDisconnected,
                smtplib.SMTPConnectError,
                smtplib.SMTPNotSupportedError,
                smtplib.SMTPResponseException,
                smtplib.SMTPException,
            ) as e:
                self.status["response_status"] = str(e)
                self.status["color_code"] = "red"
                self.categorize_email(email)
                continue

        if not self.status["isValid"]:
            self.status["response_status"] = "Unable to validate email"
            self.status["color_code"] = "red"
            self.categorize_email(email)

        self.status["email_tested"] = email
        return self.status

    def get_bounced_emails(self):
        return self.bounced_emails

    def get_valid_emails(self):
        return self.valid_emails

    def get_unsure_emails(self):
        return self.unsure_emails

    def get_undeliverable_emails(self):
        return self.undeliverable_emails

    def ensure_gdpr_compliance(self, compliant=True):
        self.gdpr_compliant = compliant


# Example usage
emails = [
    "123example@outlook.com",
]

validator = EmailExistenceValidator()
validator.ensure_gdpr_compliance(True)

for email in emails:
    result = validator.validate_email(email)
    print(f"Validation result for {email}: {result}")

print("Bounced Emails:", validator.get_bounced_emails())
print("Valid Emails:", validator.get_valid_emails())
print("Unsure Emails:", validator.get_unsure_emails())
print("Undeliverable Emails:", validator.get_undeliverable_emails())
