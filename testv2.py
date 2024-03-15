import re
import smtplib
import socket
import dns.resolver


def validate_email(email):
    status = {
        "email_tested": email,
        "isValid": False,
        "status": "",
        "response_code": 200,
        "smtp_server_message": "None",
    }

    # Step 1: Check email format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        status["status"] = "Invalid email format"
        return status

    # Step 2: Extract domain and perform MX lookup
    domain = email.split("@")[-1]
    try:
        mx_records = dns.resolver.resolve(domain, "MX")
    except dns.resolver.NoAnswer as e:
        status["status"] = f"No MX records found for domain: {str(e)}"
        return status
    except dns.resolver.NXDOMAIN as e:
        status["status"] = f"Domain does not exist: {str(e)}"
        return status
    except dns.resolver.Timeout as e:
        status["status"] = f"DNS lookup timeout: {str(e)}"
        return status

    # Step 3: Try SMTP verification
    for mx in mx_records:
        mx_host = str(mx.exchange)[:-1]
        try:
            smtp = smtplib.SMTP(mx_host, timeout=10)  # Set timeout for SMTP connection
            smtp.ehlo()  # Send EHLO command
            status_code, message = smtp.verify(email)
            smtp.quit()
            status["response_code"] = status_code
            if status_code == 250 or status_code == 252:
                status["isValid"] = True
                status["status"] = "Email is valid"
                status["smtp_server_message"] = message
            elif status_code == 550:
                status["status"] = "Recipient address rejected"
                status["smtp_server_message"] = message
            else:
                status["status"] = f"Unexpected SMTP response: {status_code}"
                status["smtp_server_message"] = message
        except smtplib.SMTPServerDisconnected as e:
            status["status"] = f"SMTP server disconnected unexpectedly: {str(e)}"
            return status
        except smtplib.SMTPConnectError as e:
            status["status"] = f"Could not connect to SMTP server: {str(e)}"
            return status
        except smtplib.SMTPNotSupportedError as e:
            status["status"] = f"SMTP server does not support verification: {str(e)}"
            return status
        except smtplib.SMTPResponseException as e:
            status["status"] = f"SMTP error: {e.smtp_code} {e.smtp_error}"
            return status
        except smtplib.SMTPException as e:
            status["status"] = f"SMTP error: {str(e)}"
            return status

    # Additional check for email address existence using email address enumeration
    try:
        with smtplib.SMTP(mx_host, timeout=10) as smtp:  # Create a new SMTP instance
            local_ip_address = socket.gethostbyname(socket.gethostname())
            source_address = (local_ip_address, 0)
            smtp.connect(
                host=mx_host, port=25, source_address=source_address
            )  # Connect to SMTP server
            smtp.ehlo()  # Send EHLO command
            status_code, message = smtp.mail("")  # Send test email
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
            status["response_code"] = status_code
            status["smtp_server_message"] = message
            if status_code == 250:
                status["isValid"] = True
                status["status"] = "Email is valid"
            elif status_code == 252:
                status["status"] = (
                    "Cannot verify recipient existence, but email is deliverable"
                )
            else:
                status["status"] = "Recipient address does not exist"
    except smtplib.SMTPException as e:
        status["isValid"] = False
        status["status"] = f"SMTP error: {str(e)}"
        # If the error message contains a code, extract it
        match = re.search(r"\b\d+\b", str(e))
        status["response_code"] = int(match.group()) if match else None

    return status


# Example usage
email = "salmantariq8385@gmail.com"
result = validate_email(email)
print(result)
