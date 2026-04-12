from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Case, F, IntegerField, OuterRef, Subquery, Sum, Value, When
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.utils import timezone

from accounts.models import Company


def signed_quantity_expression():
    return Case(
        When(movement_type=StockMovement.TYPE_IN, then=F("quantity")),
        default=F("quantity") * Value(-1),
        output_field=IntegerField(),
    )


class CompanyQuerySet(models.QuerySet):
    def for_company(self, company):
        if company is None:
            return self.none()
        return self.filter(company=company)


class ProductQuerySet(CompanyQuerySet):
    def with_stock(self):
        movement_totals = (
            StockMovement.objects.filter(product=OuterRef("pk"))
            .values("product")
            .annotate(total=Coalesce(Sum(signed_quantity_expression()), Value(0)))
            .values("total")[:1]
        )
        return self.annotate(
            current_stock=Coalesce(
                Subquery(movement_totals, output_field=IntegerField()),
                Value(0),
            )
        )

    def with_last_movement(self):
        last_movement = (
            StockMovement.objects.filter(product=OuterRef("pk"))
            .order_by("-created_at")
            .values("created_at")[:1]
        )
        return self.annotate(last_movement_at=Subquery(last_movement))


class Category(models.Model):
    company = models.ForeignKey(Company, on_delete=models.PROTECT, related_name="categories")
    name = models.CharField("nome", max_length=80)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = CompanyQuerySet.as_manager()

    class Meta:
        verbose_name = "categoria"
        verbose_name_plural = "categorias"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["company", "name"], name="unique_company_category_name"),
        ]

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    UNIT_UN = "un"
    UNIT_KG = "kg"
    UNIT_LT = "lt"
    UNIT_M = "m"

    UNIT_CHOICES = [
        (UNIT_UN, "Unidade"),
        (UNIT_KG, "Quilo"),
        (UNIT_LT, "Litro"),
        (UNIT_M, "Metro"),
    ]

    company = models.ForeignKey(Company, on_delete=models.PROTECT, related_name="products")
    name = models.CharField("nome", max_length=150)
    sku = models.CharField(max_length=60)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="categoria",
    )
    unit = models.CharField("unidade", max_length=2, choices=UNIT_CHOICES, default=UNIT_UN)
    minimum_stock = models.PositiveIntegerField("estoque minimo", default=0)
    active = models.BooleanField("ativo", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = "produto"
        verbose_name_plural = "produtos"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["company", "sku"], name="unique_company_sku"),
        ]

    def __str__(self) -> str:
        return self.name

    @property
    def stock_balance(self) -> int:
        total = self.movements.aggregate(total=Coalesce(Sum(signed_quantity_expression()), Value(0)))["total"]
        return total or 0

    @property
    def stock_status(self) -> str:
        return "baixo" if self.stock_balance <= self.minimum_stock else "normal"

    def get_absolute_url(self):
        return reverse("inventory:product-detail", args=[self.pk])


class StockMovementQuerySet(CompanyQuerySet):
    def for_company(self, company):
        if company is None:
            return self.none()
        return self.filter(company=company).select_related("product", "company", "created_by")


class StockMovement(models.Model):
    TYPE_IN = "in"
    TYPE_OUT = "out"
    TYPE_CHOICES = [
        (TYPE_IN, "Entrada"),
        (TYPE_OUT, "Saida"),
    ]

    company = models.ForeignKey(Company, on_delete=models.PROTECT, related_name="movements")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="movements")
    movement_type = models.CharField("tipo", max_length=3, choices=TYPE_CHOICES)
    quantity = models.PositiveIntegerField("quantidade")
    reason = models.CharField("motivo", max_length=120)
    notes = models.TextField("observacao", blank=True)
    created_at = models.DateTimeField("data/hora", default=timezone.now)
    created_by = models.ForeignKey(
        "auth.User",
        on_delete=models.PROTECT,
        related_name="stock_movements",
    )

    objects = StockMovementQuerySet.as_manager()

    class Meta:
        verbose_name = "movimentacao"
        verbose_name_plural = "movimentacoes"
        ordering = ["-created_at", "-id"]

    def __str__(self) -> str:
        return f"{self.get_movement_type_display()} - {self.product.name}"

    @property
    def signed_quantity(self) -> int:
        return self.quantity if self.movement_type == self.TYPE_IN else -self.quantity

    def clean(self):
        errors = {}

        if self.company_id and self.product_id and self.product.company_id != self.company_id:
            errors["product"] = "O produto precisa pertencer a mesma empresa da movimentacao."

        if self.quantity <= 0:
            errors["quantity"] = "Informe uma quantidade maior que zero."

        if self.movement_type == self.TYPE_OUT and self.product_id:
            current_balance = self.product.stock_balance
            if self.pk:
                previous = StockMovement.objects.get(pk=self.pk)
                current_balance -= previous.signed_quantity
            if self.quantity > current_balance:
                errors["quantity"] = "Saida maior que o estoque disponivel."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
