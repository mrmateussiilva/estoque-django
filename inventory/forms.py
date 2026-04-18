from django import forms
from django.core.exceptions import ValidationError

from .models import Category, Product, StockMovement


class ProductForm(forms.ModelForm):
    new_category = forms.CharField(
        label="Nova Categoria",
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "Ou crie uma nova categoria", "class": "form-dark"}
        ),
    )

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company = company
        self.fields["category"].queryset = Category.objects.for_company(
            company
        ).order_by("name")
        self.fields["category"].required = False
        self.fields["category"].empty_label = "Selecione (opcional)"

        for name, field in self.fields.items():
            if name == "active":
                field.widget.attrs["class"] = "form-check-input form-check-custom"
            elif name == "new_category":
                pass
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs["class"] = "form-dark form-select"
            else:
                field.widget.attrs["class"] = "form-dark"

        self.fields["minimum_stock"].widget.attrs["min"] = "0"
        self.fields["minimum_stock"].widget.attrs["step"] = "0.01"

        self.fields["total_metragem"].widget.attrs["step"] = "0.01"
        self.fields["total_litros"].widget.attrs["step"] = "0.01"

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get("category")
        new_category = (cleaned_data.get("new_category") or "").strip()

        if not category and not new_category:
            self.add_error("category", "Selecione uma categoria ou crie uma nova.")
        return cleaned_data

    def save(self, commit=True):
        category = self.cleaned_data.get("category")
        new_category = (self.cleaned_data.get("new_category") or "").strip()

        if not category and new_category:
            category, _ = Category.objects.get_or_create(
                company=self.company, name=new_category
            )

        self.instance.category = category
        return super().save(commit=commit)

    class Meta:
        model = Product
        fields = [
            "name",
            "sku",
            "product_type",
            "category",
            "new_category",
            "unit",
            "minimum_stock",
            "active",
            "fornecedor",
            "total_metragem",
            "quantidade_rolos",
            "tinta_tipo",
            "total_litros",
            "quantidade_baldes",
            "papel_gramatura",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={"placeholder": "Ex.: Tecido Cotton", "class": "form-dark"}
            ),
            "sku": forms.TextInput(
                attrs={"placeholder": "Ex.: TEC-COT-001", "class": "form-dark"}
            ),
            "product_type": forms.Select(attrs={"class": "form-dark form-select"}),
            "unit": forms.Select(attrs={"class": "form-dark form-select"}),
            "minimum_stock": forms.NumberInput(
                attrs={"min": "0", "step": "0.01", "class": "form-dark"}
            ),
            "fornecedor": forms.TextInput(
                attrs={"placeholder": "Nome do fornecedor", "class": "form-dark"}
            ),
            "total_metragem": forms.NumberInput(
                attrs={
                    "min": "0",
                    "step": "0.01",
                    "class": "form-dark",
                    "placeholder": "Metros",
                }
            ),
            "quantidade_rolos": forms.NumberInput(
                attrs={"min": "0", "class": "form-dark", "placeholder": "Rolos"}
            ),
            "tinta_tipo": forms.TextInput(
                attrs={"placeholder": "Ex: Acrílica, Têxtil", "class": "form-dark"}
            ),
            "total_litros": forms.NumberInput(
                attrs={
                    "min": "0",
                    "step": "0.01",
                    "class": "form-dark",
                    "placeholder": "Litros",
                }
            ),
            "quantidade_baldes": forms.NumberInput(
                attrs={"min": "0", "class": "form-dark", "placeholder": "Baldes/Latas"}
            ),
            "papel_gramatura": forms.TextInput(
                attrs={"placeholder": "Ex: 180g, 300g", "class": "form-dark"}
            ),
        }


class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = [
            "product",
            "movement_type",
            "quantity",
            "reason",
            "notes",
            "created_at",
        ]
        widgets = {
            "product": forms.Select(
                attrs={
                    "class": "form-dark form-select",
                    "placeholder": "Selecione o produto",
                }
            ),
            "movement_type": forms.Select(attrs={"class": "form-dark form-select"}),
            "quantity": forms.NumberInput(
                attrs={
                    "min": "0.001",
                    "step": "0.01",
                    "class": "form-dark",
                    "placeholder": "0",
                }
            ),
            "reason": forms.TextInput(
                attrs={
                    "placeholder": "Ex.: Compra de tinta, venda de tecido",
                    "class": "form-dark",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Detalhes opcionais sobre a movimentação",
                    "class": "form-dark",
                }
            ),
            "created_at": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-dark"}
            ),
        }

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company = company
        self.fields["product"].queryset = Product.objects.for_company(company).order_by(
            "name"
        )
        self.fields["created_at"].input_formats = ["%Y-%m-%dT%H:%M"]

        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                if "form-select" not in field.widget.attrs.get("class", ""):
                    field.widget.attrs["class"] = "form-dark form-select"
            elif field_name == "active":
                pass
            else:
                if "class" not in field.widget.attrs:
                    field.widget.attrs["class"] = "form-dark"

    def clean_product(self):
        product = self.cleaned_data["product"]
        if product.company != self.company:
            raise ValidationError("Produto inválido para esta empresa.")
        return product
