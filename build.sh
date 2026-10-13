#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

python create_admin.py

# Bake Google Sheet snapshot for HG (ORDERS + CARPET) and HETALLS into JSON files
python - <<'EOF'
import urllib.request, csv, io, json, os
from datetime import datetime

def parse_date(d_str):
    d_str = (d_str or '').strip()
    for fmt in ('%d-%b-%Y', '%b %d, %Y', '%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'):
        try:
            return datetime.strptime(d_str, fmt)
        except Exception:
            pass
    return None

def fetch_and_parse(url, sheet_type):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        raw = urllib.request.urlopen(req, timeout=20).read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Fetch {sheet_type} note: {e}")
        return []
    reader = csv.DictReader(io.StringIO(raw))
    rows = []
    for r in reader:
        ono = (r.get('Order No.') or '').strip()
        if not ono:
            continue
        od = r.get('Order Date')
        dt = parse_date(od)
        if not dt:
            continue
        portal = (r.get('Portals') or 'UNKNOWN').strip().upper()
        status_raw = (r.get('Status') or '').strip().upper()
        is_conv = 'DISPATCH' in status_raw or 'DELIVER' in status_raw
        st_label = 'Cancelled' if 'CANCEL' in status_raw else 'Dispatched' if is_conv else 'On Hold' if 'HOLD' in status_raw else 'New'
        rows.append({
            'd': dt.strftime('%Y-%m-%d'),
            'm': dt.strftime('%b %Y'),
            'mk': dt.strftime('%Y-%m'),
            'p': portal,
            's': st_label,
            'c': 1 if is_conv else 0,
            'tab': sheet_type
        })
    return rows

# 1. HG Orders + Carpet
url_hg_orders = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTkTIObrXy88vQVg2_bAI2T8vPa1tXT5IWZw8tdvF9BW7aYj9qqTA6WeZjpJHlBlw4dpTj_o7dYhtzW/pub?gid=978055065&single=true&output=csv'
url_hg_carpet = 'https://docs.google.com/spreadsheets/d/11NAw3BWNt3Bwcl1OqDv2EyL5WSLN1wZUg4qziq8SRDM/export?format=csv&gid=1394514115'
hg_rows = fetch_and_parse(url_hg_orders, 'ORDERS') + fetch_and_parse(url_hg_carpet, 'CARPET')

if hg_rows:
    with open('erp/static_dashboard_data.json', 'w', encoding='utf-8') as f:
        json.dump(hg_rows, f)
    print(f"HG Snapshot saved: {len(hg_rows)} orders (ORDERS + CARPET)")

# 2. Hetalls (Jan-2026)
url_hetalls = 'https://docs.google.com/spreadsheets/d/10SQXBuGpBnb9tDSrH287luD7h3crznnzDVhuYSF6-R8/export?format=csv&gid=277725317'
hetalls_rows = fetch_and_parse(url_hetalls, 'Jan-2026')
with open('erp/static_hetalls_data.json', 'w', encoding='utf-8') as f:
    json.dump({'rows': hetalls_rows, 'is_private': len(hetalls_rows) == 0}, f)
print(f"Hetalls Snapshot processed: {len(hetalls_rows)} orders")
EOF
