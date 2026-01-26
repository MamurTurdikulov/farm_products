from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'orders', views.OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
    path('cart/', views.CartViewSet.as_view({'get': 'list'}), name='cart-detail'),
    path('cart/add/', views.CartViewSet.as_view({'post': 'add_item'}), name='cart-add'),
    path('cart/remove/', views.CartViewSet.as_view({'post': 'remove_item'}), name='cart-remove'),
]