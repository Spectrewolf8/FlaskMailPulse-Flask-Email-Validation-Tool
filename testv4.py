# Example usage

from email_validator.EmailExistanceValidator import EmailExistenceValidator

emails = [
    "hfdjhfudhuhfushd757475@gmail.com",
    "john123@gmail.com",
    "ali@yahoo.com",
    "randomuser@hotmail.com",
    "johnjhfjdhfjdhjfhhd6666@outlook.com",
    "mogecot375@darkse.com",
]
# email = "mogecot375@darkse.com"
for email in emails:
    validator = EmailExistenceValidator()
    result = validator.validate_email(email)
    print(result)
