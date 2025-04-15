from django.db import models
from fernet_fields import EncryptedCharField
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta


# Custom User Model
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('merchant', 'Merchant'),
        ('customer', 'Customer'),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    mobile_number = models.CharField(max_length=15, null=True, blank=True)
    sensitive_info = EncryptedCharField(max_length=255, null=True, blank=True)

    is_merchant = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',
        blank=True,
    )

    def save(self, *args, **kwargs):
        if self.role == 'merchant':
            self.is_merchant = True
            self.is_customer = False
        elif self.role == 'customer':
            self.is_merchant = False
            self.is_customer = True
        else:  # Admin case
            self.is_merchant = False
            self.is_customer = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.role})"


# OTP for Password Reset (Linked to CustomUser)
class PasswordResetOTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=8)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"OTP for {self.user.email} - {self.otp_code}"


# Email-based OTP Model
class EmailOTP(models.Model):
    email = models.EmailField()
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"OTP for {self.email} - {self.otp_code}"

    def is_expired(self):
        """Check if the OTP is expired (10-minute expiration)."""
        return timezone.now() > self.created_at + timedelta(minutes=10)
