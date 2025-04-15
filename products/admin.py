from django.contrib import admin
from django.db import connection
from .models import Product, Category, Order

# Custom Admin for Order with methods to display raw encrypted data
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'total_price',
        'status',
        'created_at',
        'raw_address',  # Shows raw encrypted address
        'raw_phone'     # Shows raw encrypted phone number
    ]
    search_fields = ['user__username', 'status']
    list_filter = ['status', 'created_at']

    def raw_address(self, obj):
        """
        Retrieve the raw encrypted data stored in the 'address' field.
        """
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT address FROM {} WHERE id = %s".format(Order._meta.db_table),
                [obj.id]
            )
            row = cursor.fetchone()
        # If there's no data, row will be None or an empty string
        return row[0] if row and row[0] else "—"  # Show a dash if empty

    raw_address.short_description = 'Raw Encrypted Address'

    def raw_phone(self, obj):
        """
        Retrieve the raw encrypted data stored in the 'phone_number' field.
        """
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT phone_number FROM {} WHERE id = %s".format(Order._meta.db_table),
                [obj.id]
            )
            row = cursor.fetchone()
        return row[0] if row and row[0] else "—"  # Show a dash if empty

    raw_phone.short_description = 'Raw Encrypted Phone'

admin.site.register(Order, OrderAdmin)  # Register with the custom admin

# Register the Category model with custom admin options
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

# Register the Product model without customizations
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock', 'available', 'created_at']
    list_filter = ['available', 'category', 'created_at']
    search_fields = ['name', 'description']
