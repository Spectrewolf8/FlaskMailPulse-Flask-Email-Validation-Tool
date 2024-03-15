import re
import smtplib
import socket
import dns.resolver


def validate_email(email):
    # Initialize status dictionary with default values
    status = {
        "isValid": False,
        "status": "",
        "response_code": 200,
        "smtp_server_message": "None",
    }

    # Step 1: Check email format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        status["status"] = "Invalid email format"
        return status

    # Extract domain
    domain = email.split("@")[-1]

    # Step 2: Perform MX lookup
    try:
        mx_records = dns.resolver.resolve(domain, "MX")
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.Timeout) as e:
        status["status"] = str(e)
        return status

    # Step 3: Try SMTP verification
    for mx in mx_records:
        mx_host = str(mx.exchange)[:-1]
        try:
            with smtplib.SMTP(mx_host, timeout=10) as smtp:
                smtp.ehlo()
                status_code, message = smtp.verify(email)
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
        except (
            smtplib.SMTPServerDisconnected,
            smtplib.SMTPConnectError,
            smtplib.SMTPNotSupportedError,
            smtplib.SMTPResponseException,
            smtplib.SMTPException,
        ) as e:
            status["status"] = str(e)
            return status

    # Additional check for email address existence using email address enumeration
    try:
        with smtplib.SMTP(mx_host, timeout=10) as smtp:
            local_ip_address = socket.gethostbyname(socket.gethostname())
            source_address = (local_ip_address, 0)
            smtp.connect(host=mx_host, port=25, source_address=source_address)
            smtp.ehlo()
            status_code, message = smtp.mail("")
            print(email)
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
        status["status"] = str(e)
        match = re.search(r"\b\d+\b", str(e))
        status["response_code"] = int(match.group()) if match else None

    return status


# Example usage
email = "salmanta8385@gmail.com"
result = validate_email(email)
print(result)
