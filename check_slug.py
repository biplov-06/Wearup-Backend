import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')
django.setup()

from WearUpBack.models import Product

empty_slug_count = Product.objects.filter(slug='').count()
print(f"Products with empty slug: {empty_slug_count}")

if empty_slug_count > 0:
    print("Products with empty slug:")
    for p in Product.objects.filter(slug=''):
        print(f"ID: {p.id}, Name: {p.product_name}")
