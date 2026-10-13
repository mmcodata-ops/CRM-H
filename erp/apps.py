import csv
import io
import urllib.request
import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)

SHEET_URL = (
    'https://docs.google.com/spreadsheets/d/'
    '11NAw3BWNt3Bwcl1OqDv2EyL5WSLN1wZUg4qziq8SRDM'
    '/export?format=csv&gid=978055065'
)

PORTAL_SOURCE_MAP = {
    'AMAZON': 'AMAZON',
    'ETSY': 'ETSY',
    'SHOPIFY': 'SHOPIFY',
}


def guess_source(portal_str):
    upper = (portal_str or '').strip().upper()
    for key in PORTAL_SOURCE_MAP:
        if upper.startswith(key):
            return PORTAL_SOURCE_MAP[key]
    return 'OTHER'


def import_leads_from_sheet():
    """Download the ORDERS sheet and populate Lead table if it is empty."""
    from erp.models import Lead  # late import — DB must be ready
    from django.db.models import Count

    if Lead.objects.exists():
        logger.info("Leads already present, skipping Google Sheet import.")
        return

    logger.info("Lead table empty — downloading ORDERS sheet ...")
    try:
        with urllib.request.urlopen(SHEET_URL, timeout=30) as resp:
            raw = resp.read().decode('utf-8')
    except Exception as exc:
        logger.error("Failed to download ORDERS sheet: %s", exc)
        return

    reader = csv.DictReader(io.StringIO(raw))
    created = 0
    leads = []
    for row in reader:
        order_no = (row.get('Order No.') or '').strip()
        if not order_no:
            continue

        buyer = (row.get('Buyer Name') or '').strip().replace('\r', '').replace('\n', ' ')
        portal = (row.get('Portals') or '').strip()
        order_date = (row.get('Order Date') or '').strip()
        email = (row.get('Email') or '').strip()
        phone = (row.get('Phone') or '').strip()
        company = (row.get('Company') or portal).strip()
        status_raw = (row.get('Status') or '').strip().upper()

        source = guess_source(portal)

        if 'CANCEL' in status_raw:
            lead_status = 'LOST'
        elif 'DISPATCH' in status_raw or 'DELIVER' in status_raw:
            lead_status = 'CONVERTED'
        elif 'HOLD' in status_raw:
            lead_status = 'CONTACTED'
        else:
            lead_status = 'NEW'

        name_parts = buyer.split(None, 1) if buyer else ['Unknown']
        leads.append(Lead(
            first_name=name_parts[0],
            last_name=name_parts[1] if len(name_parts) > 1 else '',
            email=email,
            phone=phone,
            company=company,
            source=source,
            status=lead_status,
            notes=f"Order #{order_no} | Portal: {portal} | Date: {order_date}",
        ))

    if leads:
        Lead.objects.bulk_create(leads, ignore_conflicts=True)
        created = len(leads)

    logger.info("Imported %d Lead(s) from ORDERS sheet.", created)


class ErpConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'erp'

    def ready(self):
        import sys
        # Skip during management commands like migrate, collectstatic, shell
        skip_commands = {'migrate', 'makemigrations', 'collectstatic', 'shell', 'createsuperuser', 'import_google_sheet_leads'}
        if sys.argv and len(sys.argv) > 1 and sys.argv[1] in skip_commands:
            return
        import threading
        t = threading.Thread(target=import_leads_from_sheet, daemon=True)
        t.start()
