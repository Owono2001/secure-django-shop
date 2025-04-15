from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import (
    register,
    login_view,
    logout_view,
    #CustomSetupView,
    check_mfa_status,
    admin_dashboard,
    admin_statistics,
    merchant_dashboard,
    customer_dashboard,
    signup_view,
    homepage,
    account_settings,
    #cancel_2fa,
    system_logs,
    admin_user_list,
    forgot_password,
    verify_otp,
    merchant_login_view,
)

# Organized urlpatterns for clarity and better management
urlpatterns = [
    # Authentication URLs
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('signup/', signup_view, name='signup'),  # Signup URL

    # Admin Dashboard and Management
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),  # Admin Dashboard
    #path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', admin_user_list, name='admin_user_list'),  # List of users (Admin)
    path('admin/system-logs/', system_logs, name='system_logs'),  # System Logs
    path('edit_user/<int:pk>/', views.edit_user, name='edit_user'),  # Edit user
    path('delete_user/<int:pk>/', views.delete_user, name='delete_user'),  # Delete user
    #path('admin/statistics/', admin_statistics, name='admin_statistics'),

    # Merchant and Customer Dashboards
    path('merchant/dashboard/', merchant_dashboard, name='merchant_dashboard'),  # Merchant Dashboard
    path('customer/dashboard/', customer_dashboard, name='customer_dashboard'),  # Customer Dashboard
    path('customer_dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('merchant/login/', merchant_login_view, name='merchant_login'),
    # Two-Factor Authentication (2FA)
    #path('two_factor/setup/', CustomSetupView.as_view(), name='two_factor_setup'),  # Setup 2FA
    #path('check/', check_mfa_status, name='check_mfa_status'),  # Check 2FA status
    #path('account/cancel_2fa/', cancel_2fa, name='cancel_2fa'),  # Cancel 2FA setup

    # Forgot Password (OTP)
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('verify-otp/', verify_otp, name='verify_otp'),

    path('profile/', views.profile_view, name='profile'),
    path('account-settings/', account_settings, name='account_settings'),

    # Homepage
    path('', homepage, name='homepage'),  # Homepage
]

# Serve media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
