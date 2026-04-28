# Seed data script
from django.core.management.base import BaseCommand
from core.models import User, Category, Product

class Command(BaseCommand):
    help = 'Seeds initial data for MIU Campus Store'

    def handle(self, *args, **kwargs):
        # Create Manager
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123', role='MANAGER', first_name='System', last_name='Manager')
            self.stdout.write(self.style.SUCCESS('Successfully created manager: admin / admin123'))

        # Create Categories
        categories = ['Stationery', 'Electronics', 'University Merchandise', 'Books']
        cat_objs = []
        for cat_name in categories:
            cat, created = Category.objects.get_or_create(name=cat_name)
            cat_objs.append(cat)
            if created:
                self.stdout.write(f'Created category: {cat_name}')

        # Create some Products
        products = [
            {'name': 'MIU Branded Pen', 'category': cat_objs[0], 'price': 2.50, 'stock': 100},
            {'name': 'Graphing Calculator', 'category': cat_objs[1], 'price': 85.00, 'stock': 15},
            {'name': 'University Hoodie', 'category': cat_objs[2], 'price': 35.00, 'stock': 50},
            {'name': 'Notebook A4', 'category': cat_objs[0], 'price': 1.20, 'stock': 2}, # Low stock
        ]

        for p_data in products:
            Product.objects.get_or_create(
                name=p_data['name'],
                category=p_data['category'],
                defaults={
                    'price': p_data['price'],
                    'stock_quantity': p_data['stock'],
                    'description': f"High quality {p_data['name']} for MIU students."
                }
            )
        self.stdout.write(self.style.SUCCESS('Seed data loaded successfully!'))
