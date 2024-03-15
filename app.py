from flask import Flask, render_template, request, flash, redirect, url_for
from email_validator import validate_email, EmailNotValidError


app = Flask(__name__)
app.config["DEBUG"] = True


@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("index.html")


@app.route("/validate-email", methods=["GET", "POST"])
def validate_emails():
    if request.method == "POST":
        context = {"verification_results": []}
        if request.form["payload_type"] == "emails":
            # print(request.form["emails"].split(","))
            emails = request.form["emails"].split(",")
            check_deliverablility = request.form["checkDeliverability"]
            for email in emails:
                evaluation_result = evaluate_email(email, check_deliverablility)
                context["verification_results"].append(evaluation_result)

        elif request.form["payload_type"] == "email":
            email = request.form["email"]
            check_deliverablility = request.form["checkDeliverability"]
            print("check deliverability:", check_deliverablility)
            evaluation_result = evaluate_email(email, check_deliverablility)
            context["verification_results"].append(evaluation_result)

        print(context)
        return render_template(
            "results.html", verification_results=context["verification_results"]
        )

    return render_template("index.html")


# to be discarded later
@app.route("/validation-results", methods=["GET", "POST"])
def display_results():
    print(request.form)
    return render_template("results.html")


def evaluate_email(email, checkDeliverability=True):
    status = {"email": "", "status": "", "message": ""}
    try:

        # Check that the email address is valid. Turn on check_deliverability
        # for first-time validations like on account creation pages (but not
        # login pages).
        status["email"] = email
        emailinfo = validate_email(email, check_deliverability=checkDeliverability)
        print("Deilverability:", checkDeliverability)
        if checkDeliverability in "true":
            status["status"] = "Valid/deliverable"
            status["message"] = "Email is valid and deliverable"
        elif checkDeliverability in "false":
            status["status"] = "Valid"
            status["message"] = "Email is valid"

    except EmailNotValidError as e:

        # The exception message is human-readable explanation of why it's
        # not a valid (or deliverable) email address.
        print(str(e))
        status["status"] = "Invalid"
        status["message"] = str(e)
    return status


@app.route("/favicon.ico")
def favicon():
    return "", 204


if __name__ == "__main__":
    app.run()
