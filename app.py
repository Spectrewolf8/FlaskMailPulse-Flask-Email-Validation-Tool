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
        context={

        }
        if request.form["payload_type"] == "emails":
            # print(request.form["emails"].split(","))
            emails = request.form["emails"].split(",")
            for email in emails:
                 evaluate_email
            
        elif request.form["payload_type"] == "email":
            print(request.form["email"])

    return render_template("index.html")


# to be discarded later
@app.route("/validation-results", methods=["GET", "POST"])
def display_results():
    print(request.form)
    return render_template("results.html")


def evaluate_email(checkDeliverability=True):
    try:

            # Check that the email address is valid. Turn on check_deliverability
            # for first-time validations like on account creation pages (but not
            # login pages).
            emailinfo = validate_email(email, check_deliverability=checkDeliverability)

            # After this point, use only the normalized form of the email address,
            # especially before going to a database query.
            email = emailinfo.normalized
            print("Valid:", email, "\ninfo:", emailinfo)

    except EmailNotValidError as e:

            # The exception message is human-readable explanation of why it's
            # not a valid (or deliverable) email address.
            print(str(e))
 

@app.route("/favicon.ico")
def favicon():
    return "", 204


if __name__ == "__main__":
    app.run()
