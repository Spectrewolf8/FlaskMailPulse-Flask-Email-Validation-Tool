from flask import Flask, render_template, request
from email_validator import validate_email, EmailNotValidError

app = Flask(__name__)
app.config["DEBUG"] = True


@app.route("/", methods=["GET", "POST"])
def home():
    """
    Renders the home page.

    Returns:
        HTML template for the home page.
    """
    return render_template("index.html")


@app.route("/validate-email", methods=["POST"])
def validate_emails():
    """
    Validates email addresses submitted via form.

    Returns:
        HTML template displaying validation results.
    """
    if request.method == "POST":
        context = {"verification_results": []}
        payload_type = request.form.get("payload_type")

        if payload_type == "emails":
            emails = request.form.get("emails").split(",")
            check_deliverability = request.form.get("checkDeliverability")
            check_existence = request.form.get("checkExistance")

            for email in emails:
                evaluation_result = evaluate_email(
                    email, check_deliverability, check_existence
                )
                context["verification_results"].append(evaluation_result)

        elif payload_type == "email":
            email = request.form.get("email")
            check_deliverability = request.form.get("checkDeliverability")
            check_existence = request.form.get("checkExistance")
            evaluation_result = evaluate_email(
                email, check_deliverability, check_existence
            )
            context["verification_results"].append(evaluation_result)

        return render_template(
            "results.html", verification_results=context["verification_results"]
        )

    return render_template("index.html")


@app.route("/favicon.ico")
def favicon():
    """
    Route for favicon.

    Returns:
        Empty response with status code 204.
    """
    return "", 204


def evaluate_email(email, check_deliverability, check_existence):
    """
    Evaluates the validity and existence of an email address.

    Args:
        email: Email address to be evaluated.
        check_deliverability: Flag to indicate whether to check deliverability.
        check_existence: Flag to indicate whether to check existence.

    Returns:
        Dictionary containing evaluation results.
    """
    status = {
        "email": email,
        "status": "",
        "response_code": 0,
        "server_message": "None",
        "color_code": "red",
    }
    try:
        email_info = validate_email(email, check_deliverability=check_deliverability)

        if email_info.is_valid:
            if email_info.is_existent:
                status["status"] = "Valid and Existent"
            else:
                status["status"] = "Valid but Nonexistent"
        else:
            status["status"] = "Invalid"

        status["server_message"] = email_info.existance_status.get(
            "smtp_server_message", "None"
        )
        status["color_code"] = email_info.existance_status.get("color_code", "red")
        status["response_code"] = email_info.existance_status.get("response_code", 0)

    except EmailNotValidError as e:
        status["status"] = "Invalid"
        status["server_message"] = str(e)

    return status


if __name__ == "__main__":
    app.run()
