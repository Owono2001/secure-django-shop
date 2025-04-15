from django.db import models
from django.conf import settings  # to reference the custom user model
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from fernet_fields import EncryptedCharField
import bleach
from PIL import Image

# Optional, if you need dynamic user usage
User = get_user_model()  

STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('Accepted', 'Accepted'),
    ('Shipped', 'Shipped'),
    ('Delivered', 'Delivered'),
    ('Cancelled', 'Cancelled'),
]

# ----------------------------------------------------------------
# Category Model
# ----------------------------------------------------------------
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

# ----------------------------------------------------------------
# Product Model
# ----------------------------------------------------------------
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    stock = models.PositiveIntegerField(
        validators=[MinValueValidator(0)]
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.CASCADE,   # Deleting a Category also deletes its products
        null=True,
        blank=True
    )
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)

    # If you want to delete all products owned by a merchant upon merchant deletion:
    merchant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,   # <--- CASCADE if you want removing the user also removes their products
        limit_choices_to={'role': 'merchant'},
        null=True,
        blank=True
    )

    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def is_available(self):
        return self.stock > 0

    def save(self, *args, **kwargs):
        # Mark unavailable if stock = 0
        self.available = self.stock > 0

        # Sanitize description
        allowed_tags = ['p', 'b', 'i', 'u', 'strong', 'em', 'ul', 'ol', 'li']
        self.description = bleach.clean(self.description, tags=allowed_tags)

        super().save(*args, **kwargs)

        # Resize image if too large
        if self.image:
            try:
                img = Image.open(self.image.path)
                if img.height > 800 or img.width > 800:
                    output_size = (800, 800)
                    img.thumbnail(output_size)
                    img.save(self.image.path)
            except Exception as e:
                print(f"Error resizing image: {e}")

# ----------------------------------------------------------------
# Review Model
# ----------------------------------------------------------------
class Review(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    content = models.TextField()
    rating = models.PositiveSmallIntegerField()

    def save(self, *args, **kwargs):
        # Sanitize review content
        self.content = bleach.clean(self.content)
        super().save(*args, **kwargs)

# ----------------------------------------------------------------
# Order Model
# ----------------------------------------------------------------
STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('Accepted', 'Accepted'),
    ('Shipped', 'Shipped'),
    ('Delivered', 'Delivered'),
    ('Cancelled', 'Cancelled'),
]

class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    is_paid = models.BooleanField(default=False)
    
    # Single address field
    address = EncryptedCharField(max_length=255, blank=True, null=True)
    phone_number = EncryptedCharField(max_length=15, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.id} - {self.user.username} - {self.get_status_display()}"

    @property
    def is_completed(self):
        return self.status == 'Delivered'

# ----------------------------------------------------------------
# OrderItem Model
# ----------------------------------------------------------------
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE   # <--- CASCADE from order to items
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE   # Deleting a product also removes any OrderItems for it
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def get_total(self):
        return self.price * self.quantity

    def save(self, *args, **kwargs):
        if self.product.stock < self.quantity:
            raise ValueError("Not enough stock available")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"OrderItem(ID: {self.pk}) of {self.product.name} x {self.quantity}"
