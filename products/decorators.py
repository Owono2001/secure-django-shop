from django.contrib.auth.decorators import user_passes_test

# Admin Access
def admin_required(view_func):
    return user_passes_test(lambda u: u.role == 'admin')(view_func)

# Merchant Access
def merchant_required(view_func):
    return user_passes_test(lambda u: u.role == 'merchant')(view_func)

# Customer Access
def customer_required(view_func):
    return user_passes_test(lambda u: u.role == 'customer')(view_func)
