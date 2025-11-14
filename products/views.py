from django.shortcuts import render, get_object_or_404
from .models import Product

def product_list(request):
    qs = Product.objects.filter(available_kilos__gt=0).order_by("-created_at")
    q = request.GET.get("q")
    if q:
        qs = qs.filter(name__icontains=q)
    return render(request, "products/list.html", {"products": qs, "query": q})

def product_detail(request, pk):
    prod = get_object_or_404(Product, pk=pk)
    return render(request, "products/detail.html", {"product": prod})
