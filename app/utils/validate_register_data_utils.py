import re

email_regex = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")

def validate_register_data(data):
    errors = []

    email = data.get("email")
    password = data.get("password")

    if not email:
        errors.append({"field": "email", "msg": "Email is required"})
    elif not email_regex.match(email):
        errors.append({"field": "email", "msg": "Invalid email format"})

    if not password:
        errors.append({"field": "password", "msg": "Password is required"})
    elif len(password) < 6:
        errors.append({"field": "password", "msg": "Password must be at least 6 characters"})

    return errors
