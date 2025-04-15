import os
import shutil
from django.conf import settings
import django

# Setup Django environment to access settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecommerce.settings")
django.setup()

# Paths
static_images_path = os.path.join(settings.BASE_DIR, 'staticfiles', 'images')
media_images_path = os.path.join(settings.MEDIA_ROOT, 'product_images')

# Create the media directory if it doesn't exist
if not os.path.exists(media_images_path):
    os.makedirs(media_images_path)

# Copy images from static to media
for file_name in os.listdir(static_images_path):
    if file_name.endswith('.jpg'):
        shutil.copy(
            os.path.join(static_images_path, file_name),
            os.path.join(media_images_path, file_name)
        )

print("Images copied to media directory.")