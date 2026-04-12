from django.db import migrations, models
import django.db.models.deletion


def migrate_categories(apps, schema_editor):
    Category = apps.get_model("inventory", "Category")
    Product = apps.get_model("inventory", "Product")

    for product in Product.objects.all().iterator():
        legacy_name = (product.legacy_category or "").strip() or "Sem categoria"
        category, _ = Category.objects.get_or_create(
            company_id=product.company_id,
            name=legacy_name,
        )
        product.category_id = category.id
        product.save(update_fields=["category"])


class Migration(migrations.Migration):
    dependencies = [
        ("inventory", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=80, verbose_name="nome")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("company", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="categories", to="accounts.company")),
            ],
            options={
                "verbose_name": "categoria",
                "verbose_name_plural": "categorias",
                "ordering": ["name"],
            },
        ),
        migrations.RenameField(
            model_name="product",
            old_name="category",
            new_name="legacy_category",
        ),
        migrations.AddField(
            model_name="product",
            name="category",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="products", to="inventory.category", verbose_name="categoria"),
        ),
        migrations.RunPython(migrate_categories, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="product",
            name="legacy_category",
        ),
        migrations.AlterField(
            model_name="product",
            name="category",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="products", to="inventory.category", verbose_name="categoria"),
        ),
        migrations.AddConstraint(
            model_name="category",
            constraint=models.UniqueConstraint(fields=("company", "name"), name="unique_company_category_name"),
        ),
    ]
