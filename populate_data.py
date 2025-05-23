import os
import django
import json
from decimal import Decimal
from django.core.exceptions import ValidationError

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shoplift.settings")
django.setup()

from shoplift.models import Product, Category

# Load data from JSON file
with open('products.json', encoding='utf-8') as file:
    products = json.load(file)

for entry in products:
    try:
        # Ensure category exists or create it
        category_name = entry.get("category", "Uncategorized")
        category, _ = Category.objects.get_or_create(name=category_name)

        # Create Product
        Product.objects.create(
            name=entry["name"],
            price=Decimal(entry["price"]),
            category=category,
            description=entry.get("description", ""),
            rating=float(entry.get("rating", 0)),
            image_url=entry.get("image_url", ""),
            collection=entry.get("collection", "men")  # Default fallback
        )
        print(f"✅ Created: {entry['name']}")
    except (KeyError, ValidationError, Exception) as e:
        print(f"❌ Error with '{entry.get('name', 'Unknown')}': {e}")
