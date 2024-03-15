import re
import smtplib
import socket
import dns.resolver


def validate_email(email):
    status = {
        "email_tested": email,
        "isValid": False,
        "response_status": "",
        "response_code": 200,
        "smtp_server_message": "None",
    }

    # Step 1: Check email format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        status["response_status"] = "Invalid email format"
        return status

    # Step 2: Extract domain and perform MX lookup
    domain = email.split("@")[-1]
    try:
        mx_records = dns.resolver.resolve(domain, "MX")
    except (
        dns.resolver.NoAnswer,
        dns.resolver.NXDOMAIN,
        dns.resolver.Timeout,
    ) as e:
        status["response_status"] = str(e)
        return status

    # Step 3: Try SMTP verification
    for mx in mx_records:
        mx_host = str(mx.exchange)[:-1]
        try:
            with smtplib.SMTP(mx_host, timeout=10) as smtp:
                smtp.ehlo()
                status_code, message = smtp.verify(email)
                status["response_code"] = status_code
                if status_code in {250, 252}:
                    status["isValid"] = True
                    status["response_status"] = "Email is valid"
                elif status_code == 550:
                    status["response_status"] = "Recipient address rejected"
                else:
                    status["response_status"] = (
                        f"Unexpected SMTP response: {status_code}"
                    )
                status["smtp_server_message"] = message
        except (
            smtplib.SMTPServerDisconnected,
            smtplib.SMTPConnectError,
            smtplib.SMTPNotSupportedError,
            smtplib.SMTPResponseException,
            smtplib.SMTPException,
        ) as e:
            status["response_status"] = str(e)
            return status

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
            status["response_code"] = status_code
            status["smtp_server_message"] = message
            if status_code == 250:
                status["isValid"] = True
                status["response_status"] = "Email is valid"
            elif status_code == 252:
                status["response_status"] = (
                    "Cannot verify recipient existence, but email is deliverable"
                )
            else:
                status["response_status"] = "Recipient address does not exist"
    except smtplib.SMTPException as e:
        if hasattr(e, "smtp_error"):
            status["response_status"] = e.smtp_error.decode()
        else:
            status["response_status"] = str(e)
        match = re.search(r"\b\d+\b", str(e))
        status["response_code"] = int(match.group()) if match else None
        if status["response_code"] == 503:
            status["isValid"]=False

    return status


# Example usage
email = "salmantariquuuuuuu8385@gmail.com"
result = validate_email(email)
print(result)
