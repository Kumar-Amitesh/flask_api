def validate_login_data(data):
    errors = []

    if not data.get("email"):
        errors.append({"field": "email", "msg": "Email is required"})
    if not data.get("password"):
        errors.append({"field": "password", "msg": "Password is required"})

    return errors
