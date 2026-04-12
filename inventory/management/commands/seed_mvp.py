from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from accounts.models import Company, UserProfile
from inventory.models import Category, Product, StockMovement


class Command(BaseCommand):
    help = "Cria dados iniciais para demonstracao do MVP."

    def handle(self, *args, **options):
        company, _ = Company.objects.get_or_create(
            slug="empresa-demo",
            defaults={"name": "Empresa Demo"},
        )

        user, created = User.objects.get_or_create(
            username="demo",
            defaults={"email": "demo@example.com", "is_staff": True},
        )
        if created:
            user.set_password("demo1234")
            user.save()

        UserProfile.objects.get_or_create(user=user, defaults={"company": company})

        products_data = [
            {"name": "Cafe Premium 500g", "sku": "CAFE-500", "category": "Alimentos", "unit": Product.UNIT_UN, "minimum_stock": 10},
            {"name": "Acucar Cristal 1kg", "sku": "ACUCAR-1K", "category": "Alimentos", "unit": Product.UNIT_UN, "minimum_stock": 8},
            {"name": "Leite Integral 1L", "sku": "LEITE-1L", "category": "Bebidas", "unit": Product.UNIT_UN, "minimum_stock": 12},
        ]

        for item in products_data:
            category, _ = Category.objects.get_or_create(company=company, name=item["category"])
            product, _ = Product.objects.get_or_create(
                company=company,
                sku=item["sku"],
                defaults={
                    "name": item["name"],
                    "category": category,
                    "unit": item["unit"],
                    "minimum_stock": item["minimum_stock"],
                    "active": True,
                },
            )
            if product.category_id != category.id:
                product.category = category
                product.save(update_fields=["category"])
            if not product.movements.exists():
                StockMovement.objects.create(
                    company=company,
                    product=product,
                    movement_type=StockMovement.TYPE_IN,
                    quantity=25,
                    reason="Carga inicial",
                    created_by=user,
                )

        self.stdout.write(self.style.SUCCESS("Seed concluido. Usuario: demo / Senha: demo1234"))
