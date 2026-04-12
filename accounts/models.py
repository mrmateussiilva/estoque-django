from django.conf import settings
from django.db import models


class Company(models.Model):
    name = models.CharField("nome", max_length=150)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "empresa"
        verbose_name_plural = "empresas"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="users",
    )

    class Meta:
        verbose_name = "perfil de usuario"
        verbose_name_plural = "perfis de usuario"

    def __str__(self) -> str:
        return f"{self.user.get_username()} - {self.company.name}"
