from django.core.management.base import BaseCommand
from cryptography.fernet import Fernet

class Command(BaseCommand):
    help = 'Generates a new encryption key'
    
    def handle(self, *args, **kwargs):
        key = Fernet.generate_key()
        self.stdout.write(self.style.SUCCESS(f'ENCRYPTION_KEY: {key.decode()}'))