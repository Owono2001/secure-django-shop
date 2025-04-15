import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, get_backends, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.http import HttpResponseForbidden
from django.utils.dateparse import parse_date
from django.core.mail import send_mail
from django.conf import settings

# Local imports
from .forms import CustomUserCreationForm, OTPVerificationForm, ForgotPasswordForm, CustomLoginForm, MerchantLoginForm
from .models import PasswordResetOTP, CustomUser, EmailOTP
from products.models import Order, Product  # For dashboards
#from two_factor.views.core import SetupView  # Commented out - not used
from django.contrib.admin.models import LogEntry

import random


from django.conf import settings
from .forms import OTPVerificationForm
from django.utils import timezone
from datetime import timedelta
from .models import EmailOTP
from .utils import generate_secure_otp
from .forms import AccountSettingsForm
from django.contrib.auth import update_session_auth_hash  # to update session if password changes
from django import forms
# Assume you have an SMS sending function (e.g., via Twilio)
# Ensure you have a module named sms_utils.py in the same directory with a function send_sms
from .sms_utils import send_sms
from captcha.fields import CaptchaField
# Setup logger
logger = logging.getLogger(__name__)

# ----------------------------------------------------------------
# Registration (forces role="customer")
# ----------------------------------------------------------------
def register(request):
    logger.info("Register view called")
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Save with commit=False so we can override the role
            user = form.save(commit=False)
            user.role = 'customer'  # Force customer role
            user.save()

            # Authenticate & auto-login
            user = authenticate(username=user.username, password=form.cleaned_data['password1'])
            login(request, user)

            messages.success(request, "Your account has been created successfully!")
            logger.info(f"User {user.username} registered as CUSTOMER successfully.")
            return redirect_user_dashboard(user)
        else:
            messages.error(request, "Error in the form. Please correct it.")
            logger.warning("Registration form submission failed.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'users/register.html', {'form': form})


# ----------------------------------------------------------------
# Primary Login View (Only allows CUSTOMER role to log in)
# ----------------------------------------------------------------
def login_view(request):
    # Clear any old 'failed_login' flag whenever we load the page fresh
    if request.method == 'GET':
        if 'failed_login' in request.session:
            del request.session['failed_login']

    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()  # This is the authenticated user or None

            if user:
                # Check role - only 'customer' can log in here
                if user.role == 'customer':
                    login(request, user)
                    messages.success(request, "You have logged in successfully as a customer.")
                    return redirect_user_dashboard(user)
                else:
                    # Not a customer - deny login
                    messages.error(request, "Only customers can log in here.")
                    return redirect('login')
            else:
                # Authentication failed but form was valid (e.g. wrong password)
                request.session['failed_login'] = True
                messages.error(request, "Invalid username or password. Please try again.")
        else:
            # Form not valid => captcha or missing fields
            request.session['failed_login'] = True
            messages.error(request, "Login failed. Please correct any errors and try again.")
    else:
        form = CustomLoginForm()

    return render(request, 'users/login.html', {
        'form': form,
        'failed_login': request.session.get('failed_login', False),
    })


# ----------------------------------------------------------------
# Helper to route user to the right dashboard
# ----------------------------------------------------------------
def redirect_user_dashboard(user):
    logger.info(f"Redirecting user {user.username} to their dashboard.")
    if user.role == 'admin':
        return redirect('admin_dashboard')
    elif user.role == 'merchant':
        return redirect('merchant_dashboard')
    elif user.role == 'customer':
        return redirect('customer_dashboard')
    else:
        # Unrecognized role => go homepage
        return redirect('homepage')


# ----------------------------------------------------------------
# Additional Signup View (if needed)
# ----------------------------------------------------------------
def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Force role=customer or do any additional steps
            user.role = 'customer'
            user.save()
            messages.success(request, "Registration successful. Please log in.")
            return redirect('login')
        else:
            messages.error(request, "There was an error with your registration.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/signup.html', {'form': form})


# ----------------------------------------------------------------
# Logout
# ----------------------------------------------------------------
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


@login_required
def custom_logout(request):
    logger.info(f"User {request.user.username} logged out.")
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


# ----------------------------------------------------------------
# Dashboards
# ----------------------------------------------------------------
@login_required
def dashboard(request):
    """
    Generic dashboard example - but we have role-based ones anyway.
    """
    user = request.user
    if user.role == 'admin':
        return render(request, 'users/admin_dashboard.html', {'orders': Order.objects.all()[:5]})
    elif user.role == 'merchant':
        orders = Order.objects.filter(user=user)
        return render(request, 'users/merchant_dashboard.html', {'orders': orders})
    elif user.role == 'customer':
        orders = Order.objects.filter(user=user)
        return render(request, 'users/customer_dashboard.html', {'orders': orders})
    else:
        return redirect('homepage')


# Admin Dashboard
@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    # Gather statistics
    User = get_user_model()
    users = User.objects.all()
    statistics = {
        'total_users': users.count(),
        'total_merchants': users.filter(role='merchant').count(),
        'total_customers': users.filter(role='customer').count(),
        'total_orders': Order.objects.all().count(),
        'total_products': Product.objects.all().count(),
    }

    # Handle optional date filters for recent orders
    start_date = parse_date(request.GET.get('start_date'))
    end_date = parse_date(request.GET.get('end_date'))
    recent_orders = Order.objects.all().order_by('-created_at')

    if start_date and end_date:
        recent_orders = recent_orders.filter(created_at__date__range=(start_date, end_date))
    elif start_date:
        recent_orders = recent_orders.filter(created_at__date__gte=start_date)
    elif end_date:
        recent_orders = recent_orders.filter(created_at__date__lte=end_date)

    return render(request, 'users/admin_dashboard.html', {
        'statistics': statistics,
        'recent_orders': recent_orders,
        'users': users,
    })


@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_statistics(request):
    User = get_user_model()
    users = User.objects.all()
    statistics = {
        'total_users': users.count(),
        'total_merchants': users.filter(role='merchant').count(),
        'total_customers': users.filter(role='customer').count(),
        'total_orders': Order.objects.all().count(),
        'total_products': Product.objects.all().count(),
    }
    return render(request, 'users/admin_statistics.html', {'statistics': statistics})


# Merchant Dashboard
@login_required
def merchant_dashboard(request):
    logger.info(f"Merchant dashboard view called by {request.user.username}")
    # if not request.user.two_factor_completed:
    #     return redirect('two_factor_setup')
    orders = Order.objects.filter(user=request.user)
    return render(request, 'users/merchant_dashboard.html', {'orders': orders})


# Customer Dashboard
@login_required
def customer_dashboard(request):
    logger.info(f"Customer dashboard view called by {request.user.username}")
    # if not request.user.two_factor_completed:
    #     return redirect('two_factor_setup')
    orders = Order.objects.filter(user=request.user)
    return render(request, 'users/customer_dashboard.html', {'orders': orders})


def homepage(request):
    return render(request, 'homepage.html')


# Comment out any 2FA references
@login_required
def check_mfa_status(request):
    user = request.user
    if hasattr(user, 'otp_device') and user.otp_device:
        return redirect('dashboard')
    return redirect('two_factor_setup')

@login_required
def cancel_2fa(request):
    messages.info(request, "Two-Factor Authentication canceled. Returning to the homepage.")
    return redirect('homepage')

# class CustomSetupView(SetupView):
#     def done(self, form_list, **kwargs):
#         response = super().done(form_list, **kwargs)
#         user = self.request.user
#         if hasattr(user, 'otp_device') and user.otp_device:
#             logger.info(f"TOTP device created for user: {user.username}")
#         else:
#             logger.warning(f"TOTP device NOT created for user: {user.username}")
#         return redirect('dashboard')


@login_required
@user_passes_test(lambda u: u.is_staff)
def system_logs(request):
    logger.info("System logs view accessed by admin.")
    logs = LogEntry.objects.all().order_by('-action_time')[:50]
    return render(request, 'users/system_logs.html', {'logs': logs})


@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_user_list(request):
    User = get_user_model()
    users = User.objects.all()
    return render(request, 'users/admin_user_list.html', {'users': users})


@login_required
@user_passes_test(lambda u: u.is_staff)
def edit_user(request, pk):
    user = get_object_or_404(get_user_model(), pk=pk)
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            logger.info(f"Admin updated details for user: {user.username}")
            messages.success(request, "User details updated successfully.")
            return redirect('admin_dashboard')
    else:
        form = CustomUserCreationForm(instance=user)
    return render(request, 'users/edit_user.html', {'form': form, 'user': user})


@login_required
@user_passes_test(lambda u: u.is_staff)
def delete_user(request, pk):
    user = get_object_or_404(get_user_model(), pk=pk)
    if request.method == 'POST':
        if user.is_staff:
            logger.warning(f"Admin {request.user.username} attempted to delete another admin.")
            return HttpResponseForbidden("You cannot delete another admin.")
        user.delete()
        logger.info(f"Admin {request.user.username} deleted user: {user.username}")
        messages.success(request, "User deleted successfully.")
        return redirect('admin_dashboard')
    return render(request, 'users/confirm_delete_user.html', {'user': user})


# ----------------------------------------------------------------
# Forgot Password + OTP
# ----------------------------------------------------------------


def forgot_password(request):
    """
    Handles the forgot password request and sends an OTP to the user's email.
    """
    if request.method == 'POST':
        email = request.POST.get('email')

        # Check if a user with the provided email exists
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "No user found with that email address.")
            return redirect('forgot_password')

        # Generate a random OTP (6 digits)
        otp = f"{random.randint(100000, 999999)}"

        # Save the OTP in the database
        EmailOTP.objects.create(email=email, otp_code=otp, created_at=timezone.now())

        # Send the OTP to the user's email
        send_mail(
            subject="Your Password Reset OTP",
            message=f"Here is your OTP code: {otp}",
            from_email="your-email@gmail.com",
            recipient_list=[email],
            fail_silently=False,
        )

        messages.success(request, "OTP has been sent to your email address.")
        return redirect(f'/users/verify-otp/?email={email}')

    return render(request, 'users/forgot_password.html')



def verify_otp(request):
    """
    Verifies the OTP sent to the user's email and allows them to reset their password.
    """
    email = request.GET.get('email', None)

    if not email:
        messages.error(request, "Invalid access. No email provided.")
        return redirect('forgot_password')

    if request.method == 'POST':
        otp_code = request.POST.get('otp_code')
        new_password = request.POST.get('new_password')

        try:
            # Retrieve the OTP record
            otp_record = EmailOTP.objects.filter(email=email, otp_code=otp_code, is_used=False).latest('created_at')
        except EmailOTP.DoesNotExist:
            messages.error(request, "Invalid or expired OTP.")
            return redirect(f'/users/verify-otp/?email={email}')

        # Check if the OTP is still within the valid time window (e.g., 10 minutes)
        if timezone.now() > otp_record.created_at + timedelta(minutes=10):
            messages.error(request, "OTP has expired.")
            return redirect(f'/users/verify-otp/?email={email}')

        # Mark the OTP as used
        otp_record.is_used = True
        otp_record.save()

        # Reset the user's password
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
        except User.DoesNotExist:
            messages.error(request, "No user found with that email address.")
            return redirect('forgot_password')

        messages.success(request, "Your password has been reset successfully. Please log in.")
        return redirect('login')

    return render(request, 'users/verify_otp.html', {'email': email})




def account_settings(request):
    return render(request, 'users/account_settings.html')

@login_required
def profile_view(request):
    # You can display or edit user info here
    return render(request, 'users/profile.html', {'user': request.user})



def merchant_login_view(request):
    """
    Only allows 'merchant' role to log in.
    """
    if request.user.is_authenticated and request.user.role == 'merchant':
        return redirect('merchant_dashboard')

    if request.method == 'POST':
        form = MerchantLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                if user.role == 'merchant':
                    login(request, user)
                    messages.success(request, "Welcome back, Merchant!")
                    return redirect('merchant_dashboard')
                else:
                    messages.error(request, "Access denied. Only merchants can log in here.")
            else:
                messages.error(request, "Invalid merchant credentials.")
        else:
            if 'captcha' in form.errors:
                messages.error(request, "CAPTCHA verification failed. Please try again.")
    else:
        form = MerchantLoginForm()

    return render(request, 'users/merchant_login.html', {'form': form})



def generate_otp():
    return f"{random.randint(100000, 999999)}"


def send_otp_email(email):
    otp = generate_otp()
    
    # Save OTP to the EmailOTP model
    EmailOTP.objects.create(email=email, otp_code=otp, created_at=timezone.now())

    # Send the OTP via email
    send_mail(
        subject="Your OTP for Password Reset",
        message=f"Your OTP code is: {otp}",
        from_email="owonoondomangue@gmail.com",
        recipient_list=[email],
        fail_silently=False,
    )

@login_required
def account_settings(request):
    """
    Allows the user to update their account settings.
    """
    user = request.user
    if request.method == 'POST':
        form = AccountSettingsForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your account settings have been updated.")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AccountSettingsForm(instance=user)
    return render(request, 'users/account_settings.html', {'form': form})