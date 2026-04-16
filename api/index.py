import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

if os.getenv("VERCEL") and not os.getenv("DATABASE_URL") and os.getenv("VERCEL_AUTO_MIGRATE", "true").lower() == "true":
    import django
    from django.core.management import call_command

    django.setup()
    call_command("migrate", interactive=False, run_syncdb=True, verbosity=0)
    if os.getenv("VERCEL_AUTO_SEED_DEMO", "true").lower() == "true":
        call_command("seed_mvp", verbosity=0)

from config.wsgi import application

app = application
