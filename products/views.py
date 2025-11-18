from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from django.contrib import messages
from .models import Product, Customer, Order
from django.core.paginator import Paginator
from .models import Customer

def customer_list(request):
    qs = Customer.objects.all().order_by('-created_at')
    paginator = Paginator(qs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "products/customer_list.html", {
        "customers": page_obj.object_list,
        "is_paginated": page_obj.has_other_pages(),
        "page_obj": page_obj,
    })

def product_list(request):
    qs = Product.objects.filter(available_kilos__gt=0).order_by("-created_at")
    q = request.GET.get("q")
    if q:
        qs = qs.filter(name__icontains=q)
    return render(request, "products/list.html", {"products": qs, "query": q})

def product_detail(request, pk):
    prod = get_object_or_404(Product, pk=pk)
    return render(request, "products/detail.html", {"product": prod})

def order_create(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method != "POST":
        return redirect(product.get_absolute_url())

    name = request.POST.get("name", "").strip()
    surname = request.POST.get("surname", "").strip()
    phone = request.POST.get("phone", "").strip()
    email = request.POST.get("email", "").strip()
    note = request.POST.get("note", "").strip()

    try:
        kilos = float(request.POST.get("kilos", "0") or 0)
    except ValueError:
        messages.error(request, "Invalid kilos value.")
        return redirect(product.get_absolute_url())

    if kilos <= 0:
        messages.error(request, "Please specify a positive kilos amount.")
        return redirect(product.get_absolute_url())

    # Quick pre-check
    if product.available_kilos < kilos:
        messages.error(request, "Not enough stock available.")
        return redirect(product.get_absolute_url())

    # Find or create customer
    customer = None
    if phone:
        customer = Customer.objects.filter(phone=phone).first()
    if not customer and email:
        customer = Customer.objects.filter(email=email).first()

    if not customer:
        if not name:
            name = "Customer"
        customer = Customer.objects.create(name=name, surname=surname, phone=phone, email=email)

    try:
        with transaction.atomic():
            prod_locked = Product.objects.select_for_update().get(pk=product.pk)
            if prod_locked.available_kilos < kilos:
                messages.error(request, "Not enough stock available.")
                return redirect(product.get_absolute_url())

            prod_locked.available_kilos -= kilos
            prod_locked.save(update_fields=["available_kilos"])

            order = Order.objects.create(
                customer=customer,
                product=prod_locked,
                kilos_ordered=kilos,
                note=note
            )

        messages.success(request, f"Order placed successfully (#{order.pk}). Thank you!")
        return redirect(product.get_absolute_url())

    except Exception:
        messages.error(request, "An error occurred while placing the order.")
        return redirect(product.get_absolute_url())
