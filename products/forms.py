import bleach
from django import forms
from .models import Product, Order



# ✅ Product Form for adding/editing products
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'description', 'stock', 'available']  # Add 'stock' field

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),  # Stock field with minimum of 0
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_description(self):
        description = self.cleaned_data.get('description')
        allowed_tags = ['p', 'b', 'i', 'u', 'strong', 'em', 'ul', 'ol', 'li']
        return bleach.clean(description, tags=allowed_tags)


# Checkout Form for order processing (Enhanced with Shipping, Billing, and Phone Validation)
import re
from django import forms
from django.core.validators import RegexValidator
from .models import Order

class CheckoutForm(forms.ModelForm):
    # Single address field that accepts letters, numbers, commas, periods, hyphens, and spaces.
    address = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your address',
            'class': 'form-control'
        }),
        label="Address",
        validators=[RegexValidator(
            regex=r'^[a-zA-Z0-9,\.\s-]+$',
            message="Address must contain only letters, numbers, commas, periods, hyphens, and spaces."
        )]
    )
    phone_number = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your phone number',
            'class': 'form-control'
        }),
        label="Phone Number"
    )
    payment_method = forms.ChoiceField(
        choices=[('credit_card', 'Credit Card'), ('paypal', 'PayPal')],
        required=True,
        widget=forms.RadioSelect,
        label="Payment Method"
    )

    class Meta:
        model = Order
        # The Order model should have a field named 'address'
        fields = ['address', 'phone_number', 'payment_method']

    # (Optional) You can add additional custom validations in the clean method if needed.
    def clean(self):
        cleaned_data = super().clean()
        # Add any cross-field validations here if necessary.
        return cleaned_data

    # Validate phone number
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if not phone.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")
        if len(phone) < 10:
            raise forms.ValidationError("Phone number must have at least 10 digits.")
        return phone

  

        


# ✅ Product Review Form for customers to leave reviews (XSS Protected)
class ProductReviewForm(forms.Form):
    review = forms.CharField(widget=forms.Textarea, label="Write your review")

    def clean_review(self):
        data = self.cleaned_data['review']
        # Sanitize the review to remove potential XSS scripts
        allowed_tags = []
        return bleach.clean(data, tags=allowed_tags)

    
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['user', 'total_price', 'status']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove fields that no longer exist
        if 'address' in self.fields: del self.fields['address']
        if 'phone_number' in self.fields: del self.fields['phone_number']
    


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField()

class VerifyOTPForm(forms.Form):
    otp_code = forms.CharField(label="OTP Code", max_length=8)
    new_password = forms.CharField(widget=forms.PasswordInput, label="New Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("new_password")
        confirm = cleaned_data.get("confirm_password")
        if password != confirm:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['user', 'total_price', 'status']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove fields that no longer exist
        if 'address' in self.fields: del self.fields['address']
        if 'phone_number' in self.fields: del self.fields['phone_number']
    


