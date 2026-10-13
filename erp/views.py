from django.http import JsonResponse
from rest_framework import viewsets
from .models import Account, Invoice, Payment, Shipment
from .serializers import AccountSerializer, InvoiceSerializer, PaymentSerializer, ShipmentSerializer
from .templatetags.dashboard_tags import get_dashboard_stats

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

class ShipmentViewSet(viewsets.ModelViewSet):
    queryset = Shipment.objects.all()
    serializer_class = ShipmentSerializer

def dashboard_live_api(request):
    force = request.GET.get('force') == '1'
    stats = get_dashboard_stats(force_refresh=force)
    return JsonResponse(stats)
