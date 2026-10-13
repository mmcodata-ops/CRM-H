import json
import os
import csv
import io
import urllib.request
from datetime import datetime
from collections import Counter
from django import template

register = template.Library()

# HG (RugsCo) URLs
_HG_ORDERS_URL = (
    'https://docs.google.com/spreadsheets/d/e/'
    '2PACX-1vTkTIObrXy88vQVg2_bAI2T8vPa1tXT5IWZw8tdvF9BW7aYj9qqTA6WeZjpJHlBlw4dpTj_o7dYhtzW'
    '/pub?gid=978055065&single=true&output=csv'
)
_HG_CARPET_URL = (
    'https://docs.google.com/spreadsheets/d/'
    '11NAw3BWNt3Bwcl1OqDv2EyL5WSLN1wZUg4qziq8SRDM'
    '/export?format=csv&gid=1394514115'
)

# HETALLS URL
_HETALLS_URL = (
    'https://docs.google.com/spreadsheets/d/'
    '10SQXBuGpBnb9tDSrH287luD7h3crznnzDVhuYSF6-R8'
    '/export?format=csv&gid=277725317'
)

_HG_SNAPSHOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static_dashboard_data.json')
_HETALLS_SNAPSHOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static_hetalls_data.json')


def _parse_date(d_str):
    d_str = (d_str or '').strip()
    for fmt in ('%d-%b-%Y', '%b %d, %Y', '%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'):
        try:
            return datetime.strptime(d_str, fmt)
        except Exception:
            pass
    return None


def _parse_csv_rows(raw, tab_label='ORDERS'):
    reader = csv.DictReader(io.StringIO(raw))
    rows = []
    for r in reader:
        ono = (r.get('Order No.') or '').strip()
        if not ono:
            continue
        od = r.get('Order Date')
        dt = _parse_date(od)
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
            'tab': tab_label,
        })
    return rows


def _get_hg_rows():
    # 1. Try bundled snapshot
    try:
        if os.path.exists(_HG_SNAPSHOT):
            with open(_HG_SNAPSHOT, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    return data
    except Exception:
        pass

    # 2. Live fetch (both ORDERS + CARPET)
    rows = []
    try:
        req = urllib.request.Request(_HG_ORDERS_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as r:
            rows.extend(_parse_csv_rows(r.read().decode('utf-8'), 'ORDERS'))
    except Exception:
        pass

    try:
        req = urllib.request.Request(_HG_CARPET_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as r:
            rows.extend(_parse_csv_rows(r.read().decode('utf-8'), 'CARPET'))
    except Exception:
        pass

    if rows:
        try:
            with open(_HG_SNAPSHOT, 'w', encoding='utf-8') as f:
                json.dump(rows, f)
        except Exception:
            pass

    return rows


def _get_hetalls_info():
    rows = []
    is_private = False

    # 1. Try live fetch
    try:
        req = urllib.request.Request(_HETALLS_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            rows = _parse_csv_rows(r.read().decode('utf-8'), 'Jan-2026')
        is_private = False
    except Exception:
        is_private = True

    # 2. Try snapshot if live fetch failed or is private
    if not rows and os.path.exists(_HETALLS_SNAPSHOT):
        try:
            with open(_HETALLS_SNAPSHOT, 'r', encoding='utf-8') as f:
                content = json.load(f)
                if isinstance(content, dict):
                    rows = content.get('rows', [])
                    if is_private and not rows:
                        is_private = content.get('is_private', True)
        except Exception:
            pass

    if rows:
        try:
            with open(_HETALLS_SNAPSHOT, 'w', encoding='utf-8') as f:
                json.dump({'rows': rows, 'is_private': False}, f)
        except Exception:
            pass

    return rows, is_private


def _aggregate_data(rows):
    if not rows:
        return {
            'today_leads': 0, 'month_leads': 0, 'total_leads': 0, 'converted_leads': 0,
            'today_date_str': 'Today', 'current_month_str': 'This Month',
            'portal_summary': [], 'months_list': [],
            'monthly_trend': {}, 'sources': {}, 'statuses': {},
            'raw_rows': []
        }

    latest_d = max(r['d'] for r in rows)
    latest_m = max(r['mk'] for r in rows)
    latest_dt = datetime.strptime(latest_d, '%Y-%m-%d')
    today_date_str = latest_dt.strftime('%d-%b-%Y')
    current_month_str = latest_dt.strftime('%B %Y')

    today_leads = sum(1 for r in rows if r['d'] == latest_d)
    month_leads = sum(1 for r in rows if r['mk'] == latest_m)
    total_leads = len(rows)
    converted_leads = sum(r['c'] for r in rows)

    portal_counts = Counter(r['p'] for r in rows)
    unique_portals = [p for p, _ in portal_counts.most_common()]

    portal_summary = []
    sources = {}
    for p in unique_portals:
        p_rows = [r for r in rows if r['p'] == p]
        tot = len(p_rows)
        sources[p] = tot
        conv = sum(r['c'] for r in p_rows)
        tod = sum(1 for r in p_rows if r['d'] == latest_d)
        mth = sum(1 for r in p_rows if r['mk'] == latest_m)
        rate = round((conv / tot * 100), 1) if tot else 0
        portal_summary.append({
            'name': p,
            'today': tod,
            'this_month': mth,
            'total': tot,
            'converted': conv,
            'rate': rate,
        })

    statuses = {}
    for r in rows:
        statuses[r['s']] = statuses.get(r['s'], 0) + 1

    months_dict = {}
    unique_months = []
    for r in sorted(rows, key=lambda x: x['d']):
        m = r['m']
        months_dict[m] = months_dict.get(m, 0) + 1
        if m not in unique_months:
            unique_months.append(m)

    return {
        'today_leads': today_leads,
        'month_leads': month_leads,
        'total_leads': total_leads,
        'converted_leads': converted_leads,
        'today_date_str': today_date_str,
        'current_month_str': current_month_str,
        'portal_summary': portal_summary,
        'months_list': list(reversed(unique_months)),
        'monthly_trend': months_dict,
        'sources': sources,
        'statuses': statuses,
        'raw_rows': rows,
    }


@register.simple_tag
def get_dashboard_stats():
    hg_rows = _get_hg_rows()
    hetalls_rows, hetalls_is_private = _get_hetalls_info()

    hg_data = _aggregate_data(hg_rows)
    hetalls_data = _aggregate_data(hetalls_rows)

    return {
        'hg': hg_data,
        'hetalls': hetalls_data,
        'hetalls_is_private': hetalls_is_private,
        'hetalls_sheet_url': 'https://docs.google.com/spreadsheets/d/10SQXBuGpBnb9tDSrH287luD7h3crznnzDVhuYSF6-R8/edit?gid=277725317#gid=277725317',
    }
