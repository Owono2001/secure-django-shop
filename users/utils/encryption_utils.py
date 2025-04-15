from cryptography.fernet import Fernet
import base64
from django.conf import settings

class EncryptionHelper:
    def __init__(self):
        self.cipher = Fernet(settings.ENCRYPTION_KEY.encode())

    def encrypt(self, value: str) -> str:
        if not value:
            return value
        encrypted_data = self.cipher.encrypt(value.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()

    def decrypt(self, encrypted_value: str) -> str:
        if not encrypted_value:
            return encrypted_value
        encrypted_data = base64.urlsafe_b64decode(encrypted_value)
        return self.cipher.decrypt(encrypted_data).decode()

