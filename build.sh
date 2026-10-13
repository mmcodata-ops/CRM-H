#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

python create_admin.py

# Bake Google Sheet snapshot into a JSON file so the dashboard always has data
python - <<'EOF'
import urllib.request, csv, io, json, os
from datetime import datetime

url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTkTIObrXy88vQVg2_bAI2T8vPa1tXT5IWZw8tdvF9BW7aYj9qqTA6WeZjpJHlBlw4dpTj_o7dYhtzW/pub?gid=978055065&single=true&output=csv'
try:
    with urllib.request.urlopen(url, timeout=30) as r:
        raw = r.read().decode('utf-8')
    reader = csv.DictReader(io.StringIO(raw))
    rows = []
    for r in reader:
        if not (r.get('Order No.') or '').strip():
            continue
        od = (r.get('Order Date') or '').strip()
        try:
            dt = datetime.strptime(od, '%d-%b-%Y')
        except Exception:
            continue
        portal = (r.get('Portals') or '').strip().upper()
        src = 'Amazon' if portal.startswith('AMAZON') else 'Etsy' if portal.startswith('ETSY') else 'Other'
        status_raw = (r.get('Status') or '').strip().upper()
        is_conv = 'DISPATCH' in status_raw or 'DELIVER' in status_raw
        st_label = 'Cancelled' if 'CANCEL' in status_raw else 'Dispatched' if is_conv else 'On Hold' if 'HOLD' in status_raw else 'New'
        rows.append({
            'd': dt.strftime('%Y-%m-%d'),
            'm': dt.strftime('%b %Y'),
            'mk': dt.strftime('%Y-%m'),
            'p': src,
            's': st_label,
            'c': 1 if is_conv else 0
        })
    with open('erp/static_dashboard_data.json', 'w', encoding='utf-8') as f:
        json.dump(rows, f)
    print(f"Snapshot saved: {len(rows)} order rows")
except Exception as e:
    print(f"Snapshot failed (using existing): {e}")
EOF
