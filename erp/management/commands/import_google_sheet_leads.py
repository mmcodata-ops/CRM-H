import csv
import io
import sys
import urllib.request

from django.core.management.base import BaseCommand
from django.db.models import Count
from erp.models import Lead


# Map portal names from the sheet to Lead SOURCE_CHOICES
PORTAL_SOURCE_MAP = {
    'AMAZON': 'AMAZON',
    'ETSY': 'ETSY',
    'SHOPIFY': 'SHOPIFY',
}


def guess_source(portal_str):
    """Map a raw portal string like 'ETSY-CASAVANI' → 'ETSY'."""
    if not portal_str:
        return 'OTHER'
    upper = portal_str.strip().upper()
    for key in PORTAL_SOURCE_MAP:
        if upper.startswith(key):
            return PORTAL_SOURCE_MAP[key]
    return 'OTHER'


class Command(BaseCommand):
    help = "Import Leads from the ORDERS sheet of a public Google Sheet"

    def add_arguments(self, parser):
        parser.add_argument(
            '--url',
            type=str,
            default='https://docs.google.com/spreadsheets/d/11NAw3BWNt3Bwcl1OqDv2EyL5WSLN1wZUg4qziq8SRDM/edit?gid=978055065#gid=978055065',
            help='Google Sheet URL (default: the RugsCo ORDERS sheet)',
        )
        parser.add_argument('--wipe', action='store_true', help='Delete ALL existing Leads before importing')

    def handle(self, *args, **options):
        url = options['url']

        # ---- Build CSV export URL ----
        parts = url.split('/')
        try:
            sheet_id = parts[parts.index('d') + 1]
        except Exception:
            self.stderr.write(self.style.ERROR('Could not parse sheet ID from URL'))
            sys.exit(1)

        gid = '978055065'  # ORDERS tab
        if '#gid=' in url:
            gid = url.split('#gid=')[-1]
        elif '?gid=' in url:
            gid = url.split('gid=')[-1].split('&')[0].split('#')[0]

        csv_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}'
        self.stdout.write(f'Downloading ORDERS sheet -> {csv_url}')

        try:
            with urllib.request.urlopen(csv_url) as resp:
                raw = resp.read().decode('utf-8')
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Download failed: {e}'))
            sys.exit(1)

        if options['wipe']:
            deleted, _ = Lead.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Wiped {deleted} existing Lead(s)'))

        reader = csv.DictReader(io.StringIO(raw))
        created = 0
        skipped = 0

        for row in reader:
            order_no = (row.get('Order No.') or '').strip()
            if not order_no:
                skipped += 1
                continue  # skip blank rows

            buyer = (row.get('Buyer Name') or '').strip().replace('\r', '').replace('\n', ' ')
            portal = (row.get('Portals') or '').strip()
            order_date = (row.get('Order Date') or '').strip()
            email = (row.get('Email') or '').strip()
            phone = (row.get('Phone') or '').strip()
            company = (row.get('Company') or '').strip()
            status_raw = (row.get('Status') or '').strip().upper()

            source = guess_source(portal)

            # Map sheet status → Lead status
            if 'CANCEL' in status_raw:
                lead_status = 'LOST'
            elif 'DISPATCH' in status_raw or 'DELIVER' in status_raw:
                lead_status = 'CONVERTED'
            elif 'HOLD' in status_raw:
                lead_status = 'CONTACTED'
            else:
                lead_status = 'NEW'

            # Avoid duplicate: same order_no already imported
            if Lead.objects.filter(notes__contains=order_no).exists():
                skipped += 1
                continue

            # Split buyer name
            name_parts = buyer.split(None, 1) if buyer else ['Unknown']
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''

            Lead.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                company=company or portal,
                source=source,
                status=lead_status,
                notes=f"Order #{order_no} | Portal: {portal} | Date: {order_date}",
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(
            f'Done — Created {created} Lead(s), skipped {skipped} row(s)'
        ))

        # Quick summary
        summary = Lead.objects.values('source').annotate(cnt=Count('id'))
        for s in summary:
            self.stdout.write(f"  {s['source']}: {s['cnt']}")
