from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("accounts", "0001_initial"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150, verbose_name="nome")),
                ("sku", models.CharField(max_length=60)),
                ("category", models.CharField(max_length=80, verbose_name="categoria")),
                ("unit", models.CharField(choices=[("un", "Unidade"), ("kg", "Quilo"), ("lt", "Litro"), ("m", "Metro")], default="un", max_length=2, verbose_name="unidade")),
                ("minimum_stock", models.PositiveIntegerField(default=0, verbose_name="estoque minimo")),
                ("active", models.BooleanField(default=True, verbose_name="ativo")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("company", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="products", to="accounts.company")),
            ],
            options={
                "verbose_name": "produto",
                "verbose_name_plural": "produtos",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="StockMovement",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("movement_type", models.CharField(choices=[("in", "Entrada"), ("out", "Saida")], max_length=3, verbose_name="tipo")),
                ("quantity", models.PositiveIntegerField(verbose_name="quantidade")),
                ("reason", models.CharField(max_length=120, verbose_name="motivo")),
                ("notes", models.TextField(blank=True, verbose_name="observacao")),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, verbose_name="data/hora")),
                ("company", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="movements", to="accounts.company")),
                ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="stock_movements", to="auth.user")),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="movements", to="inventory.product")),
            ],
            options={
                "verbose_name": "movimentacao",
                "verbose_name_plural": "movimentacoes",
                "ordering": ["-created_at", "-id"],
            },
        ),
        migrations.AddConstraint(
            model_name="product",
            constraint=models.UniqueConstraint(fields=("company", "sku"), name="unique_company_sku"),
        ),
    ]
