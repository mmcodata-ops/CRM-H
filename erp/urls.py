from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'accounts', views.AccountViewSet)
router.register(r'invoices', views.InvoiceViewSet)
router.register(r'payments', views.PaymentViewSet)
router.register(r'shipments', views.ShipmentViewSet)

urlpatterns = [
    path('dashboard-live/', views.dashboard_live_api, name='dashboard-live'),
    path('', include(router.urls)),
]
