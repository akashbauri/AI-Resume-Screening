import re

def validate_email(email: str) -> bool:
    """
    Returns True if the email is valid.
    """

    if not email:
        return False

    email = email.strip().lower()

    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """
    Returns True if phone number looks valid.
    """

    if not phone:
        return False

    digits = re.sub(r"\D", "", phone)

    return 10 <= len(digits) <= 15
