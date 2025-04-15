from django.core.management.base import BaseCommand
from products.models import Product

IMAGE_MAP = {
    "Smart Blender": "product_images/smart_blender.jpg",
    "Standing Desk": "product_images/standing_desk.jpg",
    "Office Chair": "product_images/office_chair.jpg",
    "Desk Lamps": "product_images/desk_lamps.jpg",
    "Bookshelves": "product_images/bookshelves.jpg",
    "Filing Cabinets": "product_images/filing_cabinets.jpg",
    "Ergonomic Chairs": "product_images/ergonomic_chairs.jpg",
    "Office Desks": "product_images/office_desks.jpg",
    "Mobile Phone Holders": "product_images/mobile_phone_holders.jpg",
    "Selfie Sticks": "product_images/selfie_sticks.jpg",
    "Pop Sockets": "product_images/pop_sockets.jpg",
    "Car Chargers": "product_images/car_chargers.jpg",
    "Screen Protectors": "product_images/screen_protectors.jpg",
    "Stand Mixer": "product_images/stand_mixer.jpg",
    "Slow Cooker": "product_images/slow_cooker.jpg",
    "Rice Cooker": "product_images/rice_cooker.jpg",
    "Microwave Oven": "product_images/microwave_oven.jpg",
    "Toaster": "product_images/toaster.jpg",
    "Air Fryer": "product_images/air_fryer.jpg",
    "Blender": "product_images/blender.jpg",
    "Coffee Maker": "product_images/coffee_maker.jpg",
    "Electric Kettle": "product_images/electric_kettle.jpg",
    "Wireless Charger": "product_images/wireless_charger.jpg",
    "Power Bank": "product_images/power_bank.jpg",
    "Phone Case": "product_images/phone_case.jpg",
    "Desk Chair": "product_images/desk_chair.jpg",
    "Magnetic Phone Holder for Car": "product_images/magnetic_phone_holder.jpg",  # Added entry
}

class Command(BaseCommand):
    help = "Assign product images to products"

    def handle(self, *args, **kwargs):
        for product_name, image_path in IMAGE_MAP.items():
            try:
                product = Product.objects.get(name=product_name)
                product.image = image_path
                product.save()
                self.stdout.write(self.style.SUCCESS(f"Assigned image for {product_name}"))
            except Product.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Product not found: {product_name}"))