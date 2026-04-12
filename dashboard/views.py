from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.db.models import F, Sum, Value
from django.db.models.functions import Coalesce, TruncDate
from django.utils import timezone
from django.views.generic import TemplateView

from inventory.models import Product, StockMovement


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/home.html"

    def get_period_days(self) -> int:
        period = self.request.GET.get("period", "7")
        return int(period) if period in {"1", "7", "30"} else 7

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self.request.company
        period_days = self.get_period_days()
        since = timezone.now() - timezone.timedelta(days=period_days)

        products = Product.objects.for_company(company)
        stock_qs = products.select_related("category").with_stock().with_last_movement()
        movements = StockMovement.objects.for_company(company).select_related("product__category")
        period_movements = movements.filter(created_at__gte=since)
        low_stock_count = stock_qs.filter(active=True, current_stock__lte=F("minimum_stock")).count()
        period_entries = period_movements.filter(movement_type=StockMovement.TYPE_IN).aggregate(
            total=Coalesce(Sum("quantity"), Value(0))
        )["total"]
        period_exits = period_movements.filter(movement_type=StockMovement.TYPE_OUT).aggregate(
            total=Coalesce(Sum("quantity"), Value(0))
        )["total"]
        products_without_recent_movement = stock_qs.filter(
            models.Q(last_movement_at__lt=since) | models.Q(last_movement_at__isnull=True)
        ).count()
        daily_totals = (
            period_movements.annotate(day=TruncDate("created_at"))
            .values("day", "movement_type")
            .annotate(total=Coalesce(Sum("quantity"), Value(0)))
            .order_by("day")
        )
        entries_by_day = {}
        exits_by_day = {}
        for row in daily_totals:
            key = row["day"].strftime("%d/%m")
            if row["movement_type"] == StockMovement.TYPE_IN:
                entries_by_day[key] = row["total"]
            else:
                exits_by_day[key] = row["total"]

        chart_labels = []
        chart_entries = []
        chart_exits = []
        for offset in range(period_days - 1, -1, -1):
            day = timezone.localdate() - timezone.timedelta(days=offset)
            label = day.strftime("%d/%m")
            chart_labels.append(label)
            chart_entries.append(entries_by_day.get(label, 0))
            chart_exits.append(exits_by_day.get(label, 0))

        low_stock_products = stock_qs.filter(active=True, current_stock__lte=F("minimum_stock")).order_by("current_stock", "name")[:6]

        context.update(
            {
                "period_days": period_days,
                "total_products": products.count(),
                "low_stock_count": low_stock_count,
                "period_entries": period_entries,
                "period_exits": period_exits,
                "products_without_recent_movement": products_without_recent_movement,
                "recent_movements": movements[:8],
                "stock_summary": stock_qs.order_by("name")[:8],
                "movement_chart_labels": chart_labels,
                "movement_chart_entries": chart_entries,
                "movement_chart_exits": chart_exits,
                "low_stock_chart_labels": [product.name for product in low_stock_products],
                "low_stock_chart_values": [product.current_stock for product in low_stock_products],
            }
        )
        return context
