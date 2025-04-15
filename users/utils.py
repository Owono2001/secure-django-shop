import secrets
import string

def generate_secure_otp(length=6):
    """
    Generates a cryptographically secure numeric OTP.
    """
    digits = string.digits
    return ''.join(secrets.choice(digits) for _ in range(length))