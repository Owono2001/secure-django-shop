from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def two_factor_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # If user is authenticated but has not completed 2FA, redirect them.
        if request.user.is_authenticated and not request.user.two_factor_completed:
            messages.error(request, "Two-factor authentication is required to access this page.")
            return redirect('two_factor_setup')  # Ensure this URL name matches your 2FA setup view
        return view_func(request, *args, **kwargs)
    return _wrapped_view
