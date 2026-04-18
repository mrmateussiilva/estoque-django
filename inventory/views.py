import csv

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import ProductForm, StockMovementForm
from .models import Category, Product, StockMovement


class CompanyScopedMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.company is None:
            raise Http404("Usuario sem empresa vinculada.")
        return super().dispatch(request, *args, **kwargs)

    def is_htmx(self):
        return self.request.headers.get("HX-Request") == "true"

    def is_boosted(self):
        return self.request.headers.get("HX-Boosted") == "true"


class HTMXListMixin:
    partial_template_name = None

    def get_template_names(self):
        if self.is_htmx() and not self.is_boosted():
            return [self.partial_template_name]
        return [self.template_name]


class ProductQueryMixin(CompanyScopedMixin):
    def get_queryset(self):
        return (
            Product.objects.for_company(self.request.company)
            .select_related("category")
            .with_stock()
        )


class MovementQueryMixin(CompanyScopedMixin):
    def get_queryset(self):
        return StockMovement.objects.for_company(self.request.company).select_related(
            "product__category"
        )


class ProductListView(HTMXListMixin, ProductQueryMixin, ListView):
    model = Product
    template_name = "inventory/product_list.html"
    partial_template_name = "inventory/partials/products_table.html"
    context_object_name = "products"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get("q", "").strip()
        category_id = self.request.GET.get("category")
        active = self.request.GET.get("active")
        stock_status = self.request.GET.get("stock_status")

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(sku__icontains=search)
                | Q(category__name__icontains=search)
            )
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if active in {"true", "false"}:
            queryset = queryset.filter(active=(active == "true"))
        if stock_status == "low":
            queryset = queryset.filter(current_stock__lte=models.F("minimum_stock"))
        elif stock_status == "normal":
            queryset = queryset.filter(current_stock__gt=models.F("minimum_stock"))

        return queryset.order_by("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.for_company(self.request.company)
        context["filters"] = {
            "q": self.request.GET.get("q", ""),
            "category": self.request.GET.get("category", ""),
            "active": self.request.GET.get("active", ""),
            "stock_status": self.request.GET.get("stock_status", ""),
        }
        return context


class ProductDetailView(ProductQueryMixin, DetailView):
    model = Product
    template_name = "inventory/product_detail.html"
    context_object_name = "product"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recent_movements"] = self.object.movements.select_related(
            "created_by"
        )[:10]
        return context


class ProductCreateView(CompanyScopedMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "inventory/product_form_page.html"
    partial_template_name = "inventory/partials/modal_product_form.html"
    success_url = reverse_lazy("inventory:product-list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["company"] = self.request.company
        return kwargs

    def get_template_names(self):
        if self.is_htmx() and not self.is_boosted():
            return [self.partial_template_name]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.get_form()
        return context

    def form_valid(self, form):
        form.instance.company = self.request.company
        messages.success(self.request, "Produto criado com sucesso.")
        return super().form_valid(form)


class ProductUpdateView(ProductQueryMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "inventory/product_form_page.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["company"] = self.request.company
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Produto atualizado com sucesso.")
        return super().form_valid(form)


class MovementCreateView(CompanyScopedMixin, CreateView):
    model = StockMovement
    form_class = StockMovementForm
    template_name = "inventory/movement_form.html"
    partial_template_name = "inventory/partials/modal_movement_form.html"
    success_url = reverse_lazy("inventory:movement-list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["company"] = self.request.company
        return kwargs

    def get_template_names(self):
        if self.is_htmx() and not self.is_boosted():
            return [self.partial_template_name]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["movement_form"] = self.get_form()
        return context

    def get_initial(self):
        initial = super().get_initial()
        movement_type = self.request.GET.get("type")
        product_id = self.request.GET.get("product")
        if movement_type in {StockMovement.TYPE_IN, StockMovement.TYPE_OUT}:
            initial["movement_type"] = movement_type
        if product_id:
            initial["product"] = product_id
        return initial

    def form_valid(self, form):
        form.instance.company = self.request.company
        form.instance.created_by = self.request.user
        messages.success(self.request, "Movimentacao registrada com sucesso.")
        return super().form_valid(form)


class MovementListView(HTMXListMixin, MovementQueryMixin, ListView):
    model = StockMovement
    template_name = "inventory/movement_list.html"
    partial_template_name = "inventory/partials/movements_table.html"
    context_object_name = "movements"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        product_id = self.request.GET.get("product")
        movement_type = self.request.GET.get("type")
        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")

        if product_id:
            queryset = queryset.filter(product_id=product_id)
        if movement_type in {StockMovement.TYPE_IN, StockMovement.TYPE_OUT}:
            queryset = queryset.filter(movement_type=movement_type)
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)

        return queryset.order_by("-created_at", "-id")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["products"] = (
            Product.objects.for_company(self.request.company)
            .select_related("category")
            .order_by("name")
        )
        context["filters"] = {
            "product": self.request.GET.get("product", ""),
            "type": self.request.GET.get("type", ""),
            "start_date": self.request.GET.get("start_date", ""),
            "end_date": self.request.GET.get("end_date", ""),
        }
        return context


class StockListView(HTMXListMixin, CompanyScopedMixin, ListView):
    model = Product
    template_name = "inventory/stock_list.html"
    partial_template_name = "inventory/partials/stock_table.html"
    context_object_name = "products"
    paginate_by = 20

    def get_queryset(self):
        queryset = (
            Product.objects.for_company(self.request.company)
            .select_related("category")
            .with_stock()
        )
        search = self.request.GET.get("q", "").strip()
        category_id = self.request.GET.get("category")
        stock_status = self.request.GET.get("stock_status")
        ordering = self.request.GET.get("ordering", "name")

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(sku__icontains=search)
                | Q(category__name__icontains=search)
            )
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if stock_status == "low":
            queryset = queryset.filter(current_stock__lte=models.F("minimum_stock"))
        elif stock_status == "normal":
            queryset = queryset.filter(current_stock__gt=models.F("minimum_stock"))

        ordering_map = {
            "name": "name",
            "sku": "sku",
            "stock_desc": "-current_stock",
            "stock_asc": "current_stock",
        }
        return queryset.order_by(ordering_map.get(ordering, "name"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.for_company(self.request.company)
        context["filters"] = {
            "q": self.request.GET.get("q", ""),
            "category": self.request.GET.get("category", ""),
            "stock_status": self.request.GET.get("stock_status", ""),
            "ordering": self.request.GET.get("ordering", "name"),
        }
        return context


class CsvExportBaseView(CompanyScopedMixin, View):
    filename = "export.csv"

    def build_response(self):
        raise NotImplementedError

    def get(self, request, *args, **kwargs):
        response = self.build_response()
        response["Content-Disposition"] = f'attachment; filename="{self.filename}"'
        return response


class ProductExportView(CsvExportBaseView):
    filename = "produtos.csv"

    def build_response(self):
        queryset = ProductListView()
        queryset.request = self.request
        products = queryset.get_queryset()
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        writer = csv.writer(response)
        writer.writerow(
            [
                "Nome",
                "SKU",
                "Categoria",
                "Saldo atual",
                "Estoque minimo",
                "Status",
                "Ativo",
            ]
        )
        for product in products:
            writer.writerow(
                [
                    product.name,
                    product.sku,
                    product.category.name,
                    product.current_stock,
                    product.minimum_stock,
                    "Baixo"
                    if product.current_stock <= product.minimum_stock
                    else "Normal",
                    "Sim" if product.active else "Nao",
                ]
            )
        return response


class StockExportView(CsvExportBaseView):
    filename = "estoque_atual.csv"

    def build_response(self):
        queryset = StockListView()
        queryset.request = self.request
        products = queryset.get_queryset()
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        writer = csv.writer(response)
        writer.writerow(
            ["Produto", "SKU", "Categoria", "Saldo atual", "Estoque minimo", "Status"]
        )
        for product in products:
            writer.writerow(
                [
                    product.name,
                    product.sku,
                    product.category.name,
                    product.current_stock,
                    product.minimum_stock,
                    "Baixo"
                    if product.current_stock <= product.minimum_stock
                    else "Normal",
                ]
            )
        return response


class MovementExportView(CsvExportBaseView):
    filename = "historico_movimentacoes.csv"

    def build_response(self):
        queryset = MovementListView()
        queryset.request = self.request
        movements = queryset.get_queryset()
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        writer = csv.writer(response)
        writer.writerow(
            [
                "Data",
                "Produto",
                "SKU",
                "Categoria",
                "Tipo",
                "Quantidade",
                "Motivo",
                "Observacao",
            ]
        )
        for movement in movements:
            writer.writerow(
                [
                    timezone.localtime(movement.created_at).strftime("%d/%m/%Y %H:%M"),
                    movement.product.name,
                    movement.product.sku,
                    movement.product.category.name,
                    movement.get_movement_type_display(),
                    movement.quantity,
                    movement.reason,
                    movement.notes,
                ]
            )
        return response
