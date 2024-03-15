from email_validator import validate_email, EmailNotValidError

# email = "email@example.com"
emails = [
    "john123@gmail.com",
    "ali@yahoo.com",
    "randomuser@hotmail.com",
    "john@outlook.com",
    "example.email@aol.com",
    "random.name@icloud.com",
    "test.user@zoho.com",
    "example.name@yandex.com",
    "random.email@protonmail.com",
    "ali.abbas@cmi.ae",
    "v@safinaas.com",
    "mogecot375@darkse.com",
    "first.last@iana.org",
    "email@example.com",
    "firstname.lastname@example.com",
    "email@subdomain.example.com",
    "firstname+lastname@example.com",
    "email@123.123.123.123",
    "email@[123.123.123.123]",
    '"email"@example.com',
    "1234567890@example.com",
    "email@example-one.com",
    "_______@example.com",
    "email@example.name",
    "email@example.museum",
    "email@example.co.jp",
    "firstname-lastname@example.com",
    "much.”more\\ unusual”@example.com",
    "very.unusual.”@”.unusual.com@example.com",
    'very.”(),:;<>[]”.VERY.”very@\\ "very”.unusual@strange.example.com',
    "plainaddress",
    "#@%^%#$@#$@#.com",
    "@example.com",
    "Joe Smith <email@example.com>",
    "email.example.com",
    "email@example@example.com",
    ".email@example.com",
    "email.@example.com",
    "email..email@example.com",
    "あいうえお@example.com",
    "email@example.com (Joe Smith)",
    "email@example",
    "email@-example.com",
    "email@example.web",
    "email@111.222.333.44444",
    "email@example..com",
    "Abc..123@example.com",
]
for email in emails:
    try:

        # Check that the email address is valid. Turn on check_deliverability
        # for first-time validations like on account creation pages (but not
        # login pages).
        emailinfo = validate_email(
            email, check_deliverability=True, check_existance=True
        )

        # After this point, use only the normalized form of the email address,
        # especially before going to a database query.
        email = emailinfo.normalized
        print(
            "\ninfo:",
            emailinfo,
            "\nexistance_status:",
            emailinfo.existance_status,
            "\nexists:",
            emailinfo.is_existant,
            "\nValid:",
            emailinfo.is_valid,
        )

    except EmailNotValidError as e:

        # The exception message is human-readable explanation of why it's
        # not a valid (or deliverable) email address.
        print("error:", str(e))
