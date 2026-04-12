from django.urls import path

from .views import (
    MovementExportView,
    MovementCreateView,
    MovementListView,
    ProductExportView,
    ProductCreateView,
    ProductDetailView,
    ProductListView,
    ProductUpdateView,
    StockExportView,
    StockListView,
)


app_name = "inventory"

urlpatterns = [
    path("products/", ProductListView.as_view(), name="product-list"),
    path("products/new/", ProductCreateView.as_view(), name="product-create"),
    path("products/export/", ProductExportView.as_view(), name="product-export"),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    path("products/<int:pk>/edit/", ProductUpdateView.as_view(), name="product-update"),
    path("movements/", MovementListView.as_view(), name="movement-list"),
    path("movements/new/", MovementCreateView.as_view(), name="movement-create"),
    path("movements/export/", MovementExportView.as_view(), name="movement-export"),
    path("stock/", StockListView.as_view(), name="stock-list"),
    path("stock/export/", StockExportView.as_view(), name="stock-export"),
]
