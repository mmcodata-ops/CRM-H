from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'accounts', views.AccountViewSet)
router.register(r'invoices', views.InvoiceViewSet)  # Maps to Purchase Orders
router.register(r'payments', views.PaymentViewSet)  # Maps to Advances
router.register(r'shipments', views.ShipmentViewSet) # Maps to Goods Receipts

urlpatterns = [
    path('', include(router.urls)),
]
