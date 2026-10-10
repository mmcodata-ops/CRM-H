import json
from django import template
from django.db.models import Count
from erp.models import Lead, MasterOrder, DebitNote

register = template.Library()

@register.simple_tag
def get_dashboard_stats():
    source_data = list(Lead.objects.values('source').annotate(count=Count('id')))
    status_data = list(Lead.objects.values('status').annotate(count=Count('id')))
    
    return {
        'total_leads': Lead.objects.count(),
        'converted_leads': Lead.objects.filter(status='CONVERTED').count(),
        'total_orders': MasterOrder.objects.count(),
        'total_debit_notes': DebitNote.objects.count(),
        'sources_json': json.dumps({item['source']: item['count'] for item in source_data}),
        'statuses_json': json.dumps({item['status']: item['count'] for item in status_data}),
    }
