def validate_student(first_name, email):
    errors = []

    if not first_name.strip():
        errors.append("Имя обязательно")

    if not email.strip():
        errors.append("Email обязателен")

    if "@" not in email:
        errors.append("Некорректный email")

    return errors