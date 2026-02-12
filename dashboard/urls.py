from django.urls import path
from .views import SellerDashboardView, SellerRevenueView

app_name = 'dashboard'
urlpatterns = [
    path('seller/', SellerDashboardView.as_view(), name='seller-dashboard'),
    path('seller/revenue/', SellerRevenueView.as_view(), name='seller-revenue'),
]