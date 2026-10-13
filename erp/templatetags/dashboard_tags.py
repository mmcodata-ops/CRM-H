import json
import os
import csv
import io
import urllib.request
from django import template

register = template.Library()

# Publicly published CSV (accessible from Render and any server)
_PUBLIC_CSV = (
    'https://docs.google.com/spreadsheets/d/e/'
    '2PACX-1vTkTIObrXy88vQVg2_bAI2T8vPa1tXT5IWZw8tdvF9BW7aYj9qqTA6WeZjpJHlBlw4dpTj_o7dYhtzW'
    '/pub?gid=978055065&single=true&output=csv'
)

# Snapshot baked in by build.sh
_SNAPSHOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static_dashboard_data.json')


def _parse_csv(raw):
    reader = csv.DictReader(io.StringIO(raw))
    sources, statuses, total, converted = {}, {}, 0, 0
    for row in reader:
        if not (row.get('Order No.') or '').strip():
            continue
        total += 1
        portal = (row.get('Portals') or '').strip().upper()
        src = 'Amazon' if portal.startswith('AMAZON') else 'Etsy' if portal.startswith('ETSY') else 'Shopify' if portal.startswith('SHOPIFY') else 'Other'
        sources[src] = sources.get(src, 0) + 1
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
    return {'total_leads': total, 'converted_leads': converted, 'sources': sources, 'statuses': statuses}


def _get_data():
    # 1. Try bundled snapshot (instant, no network)
    try:
        if os.path.exists(_SNAPSHOT):
            with open(_SNAPSHOT, 'r', encoding='utf-8') as f:
                content = json.load(f)
                if content and content.get('total_leads', 0) > 0:
                    return content
    except Exception:
        pass

    # 2. Fallback: live fetch from public CSV URL
    try:
        req = urllib.request.Request(_PUBLIC_CSV, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as r:
            raw = r.read().decode('utf-8')
        data = _parse_csv(raw)
        try:
            with open(_SNAPSHOT, 'w', encoding='utf-8') as f:
                json.dump(data, f)
        except Exception:
            pass
        return data
    except Exception:
        pass

    # 3. Final fallback
    return {'total_leads': 0, 'converted_leads': 0, 'sources': {}, 'statuses': {}}


@register.simple_tag
def get_dashboard_stats():
    from erp.models import MasterOrder, DebitNote
    data = _get_data()
    return {
        'total_leads': data['total_leads'],
        'converted_leads': data['converted_leads'],
        'total_orders': MasterOrder.objects.count(),
        'total_debit_notes': DebitNote.objects.count(),
        'sources': data['sources'],
        'statuses': data['statuses'],
    }
