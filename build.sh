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

url = 'https://docs.google.com/spreadsheets/d/11NAw3BWNt3Bwcl1OqDv2EyL5WSLN1wZUg4qziq8SRDM/export?format=csv&gid=978055065'
try:
    with urllib.request.urlopen(url, timeout=30) as r:
        raw = r.read().decode('utf-8')
    reader = csv.DictReader(io.StringIO(raw))
    sources, statuses, total, converted = {}, {}, 0, 0
    for row in reader:
        order_no = (row.get('Order No.') or '').strip()
        if not order_no:
            continue
        total += 1
        portal = (row.get('Portals') or '').strip().upper()
        src = 'Amazon' if portal.startswith('AMAZON') else 'Etsy' if portal.startswith('ETSY') else 'Shopify' if portal.startswith('SHOPIFY') else 'Other'
        sources[src] = sources.get(src, 0) + 1
        status_raw = (row.get('Status') or '').strip().upper()
        if 'CANCEL' in status_raw:
            s = 'Cancelled'
        elif 'DISPATCH' in status_raw or 'DELIVER' in status_raw:
            s = 'Dispatched'; converted += 1
        elif 'HOLD' in status_raw:
            s = 'On Hold'
        else:
            s = 'New'
        statuses[s] = statuses.get(s, 0) + 1
    data = {'total_leads': total, 'converted_leads': converted, 'sources': sources, 'statuses': statuses}
    with open('erp/static_dashboard_data.json', 'w') as f:
        json.dump(data, f)
    print(f"Snapshot saved: {total} orders")
except Exception as e:
    print(f"Snapshot failed (using existing): {e}")
EOF
