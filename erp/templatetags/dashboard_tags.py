import json
import csv
import io
import urllib.request
import threading
import time
from django import template
from django.db.models import Count

register = template.Library()

# ---- In-memory cache so we only hit Google Sheet once per server process ----
_cache = {}
_cache_lock = threading.Lock()
_CACHE_TTL = 3600  # re-fetch after 1 hour

SHEET_URL = (
    'https://docs.google.com/spreadsheets/d/'
    '11NAw3BWNt3Bwcl1OqDv2EyL5WSLN1wZUg4qziq8SRDM'
    '/export?format=csv&gid=978055065'
)

PORTAL_SOURCE_MAP = {'AMAZON': 'Amazon', 'ETSY': 'Etsy', 'SHOPIFY': 'Shopify'}

def _guess_source(portal):
    upper = (portal or '').strip().upper()
    for key, label in PORTAL_SOURCE_MAP.items():
        if upper.startswith(key):
            return label
    return 'Other'


def _fetch_sheet_stats():
    """Download the ORDERS sheet and return aggregated stats dict."""
    try:
        with urllib.request.urlopen(SHEET_URL, timeout=15) as resp:
            raw = resp.read().decode('utf-8')
    except Exception:
        return None

    reader = csv.DictReader(io.StringIO(raw))
    sources = {}
    statuses = {}
    total = 0
    converted = 0

    for row in reader:
        order_no = (row.get('Order No.') or '').strip()
        if not order_no:
            continue
        total += 1
        source_label = _guess_source(row.get('Portals', ''))
        sources[source_label] = sources.get(source_label, 0) + 1

        status_raw = (row.get('Status') or '').strip().upper()
        if 'CANCEL' in status_raw:
            s = 'Cancelled'
        elif 'DISPATCH' in status_raw or 'DELIVER' in status_raw:
            s = 'Dispatched'
            converted += 1
        elif 'HOLD' in status_raw:
            s = 'On Hold'
        else:
            s = 'New'
        statuses[s] = statuses.get(s, 0) + 1

    return {
        'total_leads': total,
        'converted_leads': converted,
        'sources_json': json.dumps(sources),
        'statuses_json': json.dumps(statuses),
    }


def _get_cached_sheet_stats():
    with _cache_lock:
        cached = _cache.get('sheet_stats')
        ts = _cache.get('sheet_ts', 0)
        if cached and (time.time() - ts) < _CACHE_TTL:
            return cached
    # fetch outside the lock to avoid blocking other requests
    data = _fetch_sheet_stats()
    if data:
        with _cache_lock:
            _cache['sheet_stats'] = data
            _cache['sheet_ts'] = time.time()
        return data
    # fallback: return cached even if stale, or zeros
    return cached or {
        'total_leads': 0, 'converted_leads': 0,
        'sources_json': '{}', 'statuses_json': '{}',
    }


@register.simple_tag
def get_dashboard_stats():
    from erp.models import MasterOrder, DebitNote

    # Get lead stats live from Google Sheet (cached in memory)
    sheet = _get_cached_sheet_stats()

    return {
        'total_leads': sheet['total_leads'],
        'converted_leads': sheet['converted_leads'],
        'total_orders': MasterOrder.objects.count(),
        'total_debit_notes': DebitNote.objects.count(),
        'sources_json': sheet['sources_json'],
        'statuses_json': sheet['statuses_json'],
    }
