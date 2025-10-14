import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')
django.setup()

from WearUpBack.models import Product
from django.utils.text import slugify

# Fix existing products with empty slug
products = Product.objects.filter(slug='')
for product in products:
    product.slug = slugify(product.product_name)
    # Ensure unique
    original_slug = product.slug
    counter = 1
    while Product.objects.filter(slug=product.slug).exclude(pk=product.pk).exists():
        product.slug = f"{original_slug}-{counter}"
        counter += 1
    product.save()
    print(f"Updated product {product.id}: {product.product_name} -> {product.slug}")

print("All empty slugs fixed.")
