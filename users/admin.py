from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, EmailOTP
from axes.models import AccessAttempt
from axes.admin import AccessAttemptAdmin as DefaultAccessAttemptAdmin
from axes.handlers.proxy import AxesProxyHandler


# Custom User Admin for managing users
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    
    # Display these fields in the user list in the Django admin panel
    list_display = ('username', 'email', 'role', 'is_active', 'is_staff', 'last_login', 'date_joined')

    # Add filtering by role and active status
    list_filter = ('role', 'is_active', 'is_staff')

    # Customize the user edit page to include the role field
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )

    # Customize the user creation form to include the role field
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role', 'email')}),  # Add role to creation form
    )

    # Allow searching by username and email in the admin panel
    search_fields = ('username', 'email')
    ordering = ('username',)  # Sort by username by default


# Unregister existing AccessAttempt to avoid AlreadyRegistered error
try:
    admin.site.unregister(AccessAttempt)
except admin.sites.NotRegistered:
    pass


# Customize the AccessAttempt admin
class CustomAccessAttemptAdmin(DefaultAccessAttemptAdmin):
    list_display = ('username', 'ip_address', 'failures_since_start', 'attempt_time')
    search_fields = ('username', 'ip_address')
    list_filter = ('attempt_time', 'failures_since_start')
    ordering = ('-attempt_time',)
    actions = ['unlock_users']

    def unlock_users(self, request, queryset):
        for attempt in queryset:
            AxesProxyHandler.reset_attempt(username=attempt.username)
        self.message_user(request, "Selected users have been unlocked.", messages.SUCCESS)


# Re-register with the custom admin
admin.site.register(AccessAttempt, CustomAccessAttemptAdmin)


# Register the CustomUser model to the admin site
admin.site.register(CustomUser, CustomUserAdmin)


@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ('email', 'otp_code', 'created_at', 'is_used')
    search_fields = ('email', 'otp_code')
    list_filter = ('is_used',)

