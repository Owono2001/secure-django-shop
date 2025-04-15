from django.contrib.auth import get_user

def enforce_mfa(get_response):
    def middleware(request):
        user = get_user(request)
        if user.is_authenticated:
            print(f"User {user.username} logged in.")
        return get_response(request)

    return middleware