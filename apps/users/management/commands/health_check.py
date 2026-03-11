# ton_app/management/commands/health_check.py
from django.core.management.base import BaseCommand
from django.db import connection
import requests
import json


class Command(BaseCommand):
    help = "Vérifie la santé de l'application et de la BDD"

    def handle(self, *args, **options):
        status = {
            "app": "ok",
            "database": "unknown",
            "supabase": "unknown",
            "timestamp": None,
        }

        try:
            # Test BDD
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            status["database"] = "connected"
            self.stdout.write(self.style.SUCCESS("✓ BDD connectée"))
        except Exception as e:
            status["database"] = f"error: {str(e)}"
            self.stdout.write(self.style.ERROR("✗ BDD erreur"))

        # Si tu veux aussi ping Supabase direct depuis Django
        try:
            supabase_url = "https://vpythidfoyciubozmxaw.supabase.co"
            response = requests.get(f"{supabase_url}/rest/v1/", timeout=5)
            if response.status_code == 200:
                status["supabase"] = "ok"
                self.stdout.write(self.style.SUCCESS("✓ Supabase répond"))
        except:
            status["supabase"] = "no response"

        self.stdout.write(json.dumps(status, indent=2))
