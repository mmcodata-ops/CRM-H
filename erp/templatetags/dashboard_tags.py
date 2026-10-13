import json
import os
from django import template
from django.db.models import Count

register = template.Library()

# Bundled snapshot baked in at deploy time by build.sh
_SNAPSHOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static_dashboard_data.json')


def _load_snapshot():
    try:
        with open(_SNAPSHOT) as f:
            return json.load(f)
    except Exception:
        return None


@register.simple_tag
def get_dashboard_stats():
    from erp.models import MasterOrder, DebitNote

    data = _load_snapshot() or {
        'total_leads': 0, 'converted_leads': 0,
        'sources': {}, 'statuses': {},
    }

    return {
        'total_leads': data['total_leads'],
        'converted_leads': data['converted_leads'],
        'total_orders': MasterOrder.objects.count(),
        'total_debit_notes': DebitNote.objects.count(),
        'sources_json': json.dumps(data['sources']),
        'statuses_json': json.dumps(data['statuses']),
    }
