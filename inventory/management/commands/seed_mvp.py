from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from accounts.models import Company, UserProfile


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

        self.stdout.write(
            self.style.SUCCESS("Seed concluido. Usuario: demo / Senha: demo1234")
        )
