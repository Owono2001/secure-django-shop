from django.contrib import admin
from django.urls import path, include
from products.views import homepage
from django.contrib.auth.views import LoginView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),  # Users app
    path('products/', include('products.urls')),  # Products app
    #path('account/', include('two_factor.urls', namespace='two_factor')),  # Django Two-Factor
    path('accounts/', include('allauth.urls')),  # <--- This is required for allauth
    path('', homepage, name='homepage'),  # Homepage
    

    # Add the captcha URLs for django-simple-captcha:
    path('captcha/', include('captcha.urls')),
]
# Serve media files during development
if settings.DEBUG:
    from django.conf import settings
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)