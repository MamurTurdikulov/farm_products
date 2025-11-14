# products/api_urls.py
from django.urls import path
from . import api_views

urlpatterns = [
    path("products/", api_views.ProductListCreateAPIView.as_view(), name="api_products_list_create"),
    path("products/<int:pk>/", api_views.ProductDetailAPIView.as_view(), name="api_products_detail"),
    path("customers/", api_views.CustomerListCreateAPIView.as_view(), name="api_customers"),
    path("customers/<int:pk>/", api_views.CustomerDetailAPIView.as_view(), name="api_customer_detail"),
    path("orders/", api_views.OrderListCreateAPIView.as_view(), name="api_orders"),
    path("orders/<int:pk>/", api_views.OrderDetailAPIView.as_view(), name="api_order_detail"),
]
