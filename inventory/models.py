from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Case, DecimalField, F, OuterRef, Subquery, Sum, Value, When
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.utils import timezone

from accounts.models import Company


def signed_quantity_expression():
    return Case(
        When(movement_type=StockMovement.TYPE_IN, then=F("quantity")),
        default=F("quantity") * Value(-1),
        output_field=DecimalField(max_digits=12, decimal_places=3),
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
            .annotate(
                total=Coalesce(
                    Sum(signed_quantity_expression()),
                    Value(
                        0, output_field=DecimalField(max_digits=12, decimal_places=3)
                    ),
                )
            )
            .values("total")[:1]
        )
        return self.annotate(
            current_stock=Coalesce(
                Subquery(
                    movement_totals,
                    output_field=DecimalField(max_digits=12, decimal_places=3),
                ),
                Value(0, output_field=DecimalField(max_digits=12, decimal_places=3)),
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
    company = models.ForeignKey(
        Company, on_delete=models.PROTECT, related_name="categories"
    )
    name = models.CharField("nome", max_length=80)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = CompanyQuerySet.as_manager()

    class Meta:
        verbose_name = "categoria"
        verbose_name_plural = "categorias"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "name"], name="unique_company_category_name"
            ),
        ]

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    TYPE_TECIDO = "tecido"
    TYPE_TINTA = "tinta"
    TYPE_PAPEL = "papel"
    TYPE_GERAL = "geral"

    TYPE_CHOICES = [
        (TYPE_TECIDO, "Tecido"),
        (TYPE_TINTA, "Tinta"),
        (TYPE_PAPEL, "Papel"),
        (TYPE_GERAL, "Geral (Aviamentos)"),
    ]

    UNIT_UN = "un"
    UNIT_MT = "mt"
    UNIT_LT = "lt"
    UNIT_KG = "kg"
    UNIT_FL = "fl"
    UNIT_PC = "pc"
    UNIT_ROLO = "rolo"

    UNIT_CHOICES = [
        (UNIT_UN, "Unidade (UN)"),
        (UNIT_MT, "Metros (MT)"),
        (UNIT_LT, "Litros (LT)"),
        (UNIT_KG, "Quilos (KG)"),
        (UNIT_FL, "Folhas (FL)"),
        (UNIT_PC, "Peças (PC)"),
        (UNIT_ROLO, "Rolos"),
    ]

    UNIT_SUFFIX_MAP = {
        UNIT_UN: "UN",
        UNIT_MT: "MT",
        UNIT_LT: "LT",
        UNIT_KG: "KG",
        UNIT_FL: "FL",
        UNIT_PC: "PC",
        UNIT_ROLO: "RL",
    }

    company = models.ForeignKey(
        Company, on_delete=models.PROTECT, related_name="products"
    )
    name = models.CharField("nome", max_length=150)
    sku = models.CharField(max_length=60)
    product_type = models.CharField(
        "tipo de material",
        max_length=10,
        choices=TYPE_CHOICES,
        default=TYPE_GERAL,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="categoria",
        blank=True,
        null=True,
    )
    unit = models.CharField(
        "unidade", max_length=4, choices=UNIT_CHOICES, default=UNIT_UN
    )
    minimum_stock = models.DecimalField(
        "estoque minimo", max_digits=12, decimal_places=3, default=0
    )
    active = models.BooleanField("ativo", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    fornecedor = models.CharField(
        "fornecedor",
        max_length=150,
        blank=True,
        null=True,
        help_text="Fornecedor do material",
    )

    total_metragem = models.DecimalField(
        "metragem total (m)",
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Metragem total em metros (para Tecidos e Papéis)",
    )
    quantidade_rolos = models.PositiveIntegerField(
        "quantidade de rolos",
        blank=True,
        null=True,
        help_text="Número de rolos (para Tecidos e Papéis)",
    )

    tinta_tipo = models.CharField(
        "tipo de tinta",
        max_length=50,
        blank=True,
        null=True,
        help_text="Ex: Acrílica, Têxtil, Serigráfica",
    )
    total_litros = models.DecimalField(
        "litros total",
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Volume total em litros (para Tintas)",
    )
    quantidade_baldes = models.PositiveIntegerField(
        "quantidade de baldes/latas",
        blank=True,
        null=True,
        help_text="Número de baldes ou latas (para Tintas)",
    )

    papel_gramatura = models.CharField(
        "gramatura (g/m²)",
        max_length=20,
        blank=True,
        null=True,
        help_text="Gramatura do papel (ex: 180g, 300g)",
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = "produto"
        verbose_name_plural = "produtos"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "sku"], name="unique_company_sku"
            ),
        ]

    def __str__(self) -> str:
        return self.name

    @property
    def unit_suffix(self) -> str:
        return self.UNIT_SUFFIX_MAP.get(self.unit, "UN")

    @property
    def stock_balance(self):
        total = self.movements.aggregate(
            total=Coalesce(Sum(signed_quantity_expression()), Value(0))
        )["total"]
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
        return self.filter(company=company).select_related(
            "product", "company", "created_by"
        )


class StockMovement(models.Model):
    TYPE_IN = "in"
    TYPE_OUT = "out"
    TYPE_CHOICES = [
        (TYPE_IN, "Entrada"),
        (TYPE_OUT, "Saida"),
    ]

    company = models.ForeignKey(
        Company, on_delete=models.PROTECT, related_name="movements"
    )
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="movements"
    )
    movement_type = models.CharField("tipo", max_length=3, choices=TYPE_CHOICES)
    quantity = models.DecimalField("quantidade", max_digits=12, decimal_places=3)
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
    def signed_quantity(self):
        return self.quantity if self.movement_type == self.TYPE_IN else -self.quantity

    def clean(self):
        errors = {}

        if (
            self.company_id
            and self.product_id
            and self.product.company_id != self.company_id
        ):
            errors["product"] = (
                "O produto precisa pertencer a mesma empresa da movimentacao."
            )

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
