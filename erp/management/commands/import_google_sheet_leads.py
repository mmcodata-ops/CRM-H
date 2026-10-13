import csv
import io
import sys
import urllib.request
from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone
from erp.models import Lead

class Command(BaseCommand):
    help = "Import Leads from a public Google Sheet (CSV export)"

    def add_arguments(self, parser):
        parser.add_argument('sheet_url', type=str, help='Public Google Sheet URL')
        parser.add_argument('--gid', type=str, default=None, help='Sheet GID (optional, overrides URL param)')

    def handle(self, *args, **options):
        url = options['sheet_url']
        gid = options.get('gid')
        # Convert to CSV export URL
        if 'docs.google.com/spreadsheets/d/' not in url:
            self.stderr.write(self.style.ERROR('Not a valid Google Sheet URL'))
            sys.exit(1)
        # Extract the sheet ID
        parts = url.split('/')
        try:
            sheet_id = parts[parts.index('d') + 1]
        except Exception:
            self.stderr.write(self.style.ERROR('Could not parse sheet ID'))
            sys.exit(1)
        # Determine gid
        if not gid:
            # try to find gid in the URL fragment
            if '#gid=' in url:
                gid = url.split('#gid=')[-1]
            else:
                gid = '0'
        csv_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}'
        self.stdout.write(f'Downloading CSV from {csv_url}')
        try:
            with urllib.request.urlopen(csv_url) as response:
                raw = response.read().decode('utf-8')
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Failed to download CSV: {e}'))
            sys.exit(1)
        reader = csv.DictReader(io.StringIO(raw))
        created = 0
        for row in reader:
            # Expected column names – adjust if your sheet differs
            first_name = row.get('First Name') or row.get('first_name') or ''
            last_name = row.get('Last Name') or row.get('last_name') or ''
            email = row.get('Email') or row.get('email') or ''
            phone = row.get('Phone') or row.get('phone') or ''
            company = row.get('Company') or row.get('company') or ''
            source = row.get('Source') or row.get('source') or 'OTHER'
            # Optional order date – we store it in notes if present
            order_date = row.get('Order Date') or row.get('order_date')
            notes = f"Imported from Google Sheet on {timezone.now().strftime('%Y-%m-%d %H:%M')}"
            if order_date:
                notes += f" | Order Date: {order_date}"
            # Avoid duplicates (simple heuristic: same email + source)
            if email and Lead.objects.filter(email=email, source=source).exists():
                continue
            Lead.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                company=company,
                source=source,
                notes=notes,
            )
            created += 1
        self.stdout.write(self.style.SUCCESS(f'Created {created} new Lead(s) from the sheet'))
