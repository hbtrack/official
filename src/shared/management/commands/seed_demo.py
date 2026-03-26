"""Management command: python manage.py seed_demo"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Popula o banco com dados demo para desenvolvimento local."

    def handle(self, *args, **options):
        self.stdout.write("Executando seed demo…")
        from scripts.seed import seed
        seed()
