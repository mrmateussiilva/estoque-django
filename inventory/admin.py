from django.contrib import admin

from .models import Category, Product, StockMovement


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "created_at")
    list_filter = ("company",)
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "sku", "category", "unit", "minimum_stock", "active")
    list_filter = ("company", "active", "category", "unit")
    search_fields = ("name", "sku", "category__name")


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("product", "company", "movement_type", "quantity", "reason", "created_at", "created_by")
    list_filter = ("company", "movement_type", "created_at")
    search_fields = ("product__name", "product__sku", "reason", "notes")
    list_select_related = ("product", "company", "created_by")
