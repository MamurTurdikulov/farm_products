from django.urls import path
from . import views

urlpatterns = [
    path("categories/", views.CategoryViewSet.as_view({
        "get": "list",
        "post": "create"
    })),
    path("categories/<int:pk>/", views.CategoryViewSet.as_view({
        "get": "retrieve",
        "put": "update",
        "delete": "destroy"
    })),

    path("products/", views.ProductViewSet.as_view({
        "get": "list",
        "post": "create"
    })),
    path("products/<int:pk>/", views.ProductViewSet.as_view({
        "get": "retrieve",
        "put": "update",
        "delete": "destroy"
    })),

    path("orders/", views.OrderViewSet.as_view({"get": "list"})),
    path("orders/<int:pk>/", views.OrderViewSet.as_view({
        "get": "retrieve",
        "patch": "partial_update"
    })),
]