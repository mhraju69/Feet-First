from django.apps import AppConfig
from django.db.utils import OperationalError, ProgrammingError


class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Products'
    def ready(self):
        import Products.signal
        from .models import Category, SubCategory
        # categories.py

        CATEGORIES = [
            {"slug": "everyday-shoes", "name": "Everyday Shoes"},
            {"slug": "sports-shoes", "name": "Sports Shoes"},
        ]

        SUBCATEGORIES = [
        # Everyday Shoes
                {"slug": "casual-sneaker", "name": "Casual Sneaker", "category": "everyday-shoes"},
                {"slug": "elegant-shoes", "name": "Elegant Shoes", "category": "everyday-shoes"},
                {"slug": "comfortable-shoes", "name": "Comfortable Shoes", "category": "everyday-shoes"},
                {"slug": "sandals", "name": "Sandals", "category": "everyday-shoes"},
                {"slug": "work-shoes", "name": "Work Shoes", "category": "everyday-shoes"},
                {"slug": "miscellaneous", "name": "Miscellaneous", "category": "everyday-shoes"},

                # Sports Shoes
                {"slug": "running-shoes", "name": "Running Shoes", "category": "sports-shoes"},
                {"slug": "cycling-shoes", "name": "Cycling Shoes", "category": "sports-shoes"},
                {"slug": "hockey-shoes", "name": "Hockey Shoes", "category": "sports-shoes"},
                {"slug": "ski-boots", "name": "Ski Boots", "category": "sports-shoes"},
                {"slug": "basketball-shoes", "name": "Basketball Shoes", "category": "sports-shoes"},
                {"slug": "golf-shoes", "name": "Golf Shoes", "category": "sports-shoes"},
                {"slug": "football-shoes", "name": "Football Shoes", "category": "sports-shoes"},
                {"slug": "tennis-shoes", "name": "Tennis Shoes", "category": "sports-shoes"},
                {"slug": "climbing-shoes", "name": "Climbing Shoes", "category": "sports-shoes"},
                {"slug": "mountain-trekking-shoes", "name": "Mountain Trekking Shoes", "category": "sports-shoes"},
            ]

        try:
            for cat in CATEGORIES:
                Category.objects.get_or_create(slug=cat['slug'], defaults={'name': cat['name']})

            for sub in SUBCATEGORIES:
                category = Category.objects.get(slug=sub['category'])
                SubCategory.objects.get_or_create(
                    slug=sub['slug'],
                    defaults={
                        'name': sub['name'],
                        'category': category
                    }
                )
        except (OperationalError, ProgrammingError):
            pass  
