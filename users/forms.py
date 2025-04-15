from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from captcha.fields import CaptchaField
from .models import CustomUser

# -----------------------------------------------------------
# Custom Login Form with reCAPTCHA (for customers)
# -----------------------------------------------------------
class CustomLoginForm(AuthenticationForm):
    captcha = CaptchaField(
        error_messages={
            'invalid': 'Incorrect, please try again.',
            'required': 'Please complete the CAPTCHA to prove you are not a robot.'
        }
    )


# -----------------------------------------------------------
# Public Register Form (Customer Only)
# -----------------------------------------------------------
class CustomUserCreationForm(UserCreationForm):
    """
    Only allows 'customer' as the role.
    """
    captcha = CaptchaField(
        error_messages={
            'invalid': 'Incorrect, please try again.',
            'required': 'Please complete the CAPTCHA to prove you are not a robot.'
        }
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
        help_text="A valid email address is required."
    )
    username = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your username'}),
        help_text="Enter your desired username."
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'}),
        label="Password",
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm your password'}),
        label="Confirm Password",
    )
    role = forms.ChoiceField(
        choices=[('customer', 'Customer')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Role",
        help_text="You will be registered as a customer."
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'role', 'captcha')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return password2

    def clean_role(self):
        # Force the role to 'customer'
        return 'customer'


# -----------------------------------------------------------
# Forgot Password Form (Mobile OTP)
# -----------------------------------------------------------
class ForgotPasswordForm(forms.Form):
    mobile_number = forms.CharField(label="Mobile Number", max_length=15)
    
    def clean_mobile_number(self):
        mobile = self.cleaned_data['mobile_number']
        # Strip whitespace and ensure it is in E.164 format (starting with '+')
        mobile = mobile.strip()
        if not mobile.startswith('+'):
            mobile = '+' + mobile
        return mobile


# -----------------------------------------------------------
# OTP Verification Form (Mobile OTP + Password Reset)
# -----------------------------------------------------------
class OTPVerificationForm(forms.Form):
    mobile_number = forms.CharField(label="Mobile Number", max_length=15)
    otp_code = forms.CharField(label="OTP Code", max_length=6)
    new_password = forms.CharField(widget=forms.PasswordInput, label="New Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    captcha = CaptchaField(label="Captcha")

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("new_password")
        confirm = cleaned_data.get("confirm_password")
        if password != confirm:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data


# -----------------------------------------------------------
# Merchant Login Form with reCAPTCHA
# -----------------------------------------------------------
class MerchantLoginForm(forms.Form):
    username = forms.CharField(
        label="Merchant Username",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    captcha = CaptchaField(
        error_messages={
            'invalid': 'Incorrect, please try again.',
            'required': 'Please complete the CAPTCHA to prove you are not a robot.'
        }
    )


class AccountSettingsForm(forms.ModelForm):
    captcha = CaptchaField(label="Captcha", required=False)  # Optional security field

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'mobile_number']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def clean_mobile_number(self):
        mobile = self.cleaned_data.get('mobile_number')
        if mobile:
            mobile = mobile.strip()
            if not mobile.startswith('+'):
                mobile = '+' + mobile
        return mobile