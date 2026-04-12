from django import forms
from django.core.exceptions import ValidationError

from .models import Category, Product, StockMovement


class ProductForm(forms.ModelForm):
    new_category = forms.CharField(
        label="nova categoria",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Ou crie uma nova categoria"}),
    )

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company = company
        self.fields["category"].queryset = Category.objects.for_company(company).order_by("name")
        self.fields["category"].required = False

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
            category, _ = Category.objects.get_or_create(company=self.company, name=new_category)

        self.instance.category = category
        return super().save(commit=commit)

    class Meta:
        model = Product
        fields = ["name", "sku", "category", "new_category", "unit", "minimum_stock", "active"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Ex.: Cafe Premium 500g"}),
            "sku": forms.TextInput(attrs={"placeholder": "Ex.: CAFE-500"}),
            "minimum_stock": forms.NumberInput(attrs={"min": 0}),
        }


class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ["product", "movement_type", "quantity", "reason", "notes", "created_at"]
        widgets = {
            "quantity": forms.NumberInput(attrs={"min": 1}),
            "reason": forms.TextInput(attrs={"placeholder": "Ex.: Compra, venda, ajuste inicial"}),
            "notes": forms.Textarea(attrs={"rows": 3, "placeholder": "Detalhes opcionais"}),
            "created_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company = company
        self.fields["product"].queryset = Product.objects.for_company(company).order_by("name")
        self.fields["created_at"].input_formats = ["%Y-%m-%dT%H:%M"]

    def clean_product(self):
        product = self.cleaned_data["product"]
        if product.company != self.company:
            raise ValidationError("Produto invalido para esta empresa.")
        return product
