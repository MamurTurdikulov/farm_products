import json

from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import *
from .services import *
from config.settings import MEDIA_ROOT
from .forms import *


def home_page(request):
    """
    Returns a single product (as JSON) by its ID from GET parameters.
    """
    if request.GET:
        product = get_product_by_id(request.GET.get("product_id", 0))
        return JsonResponse(product or {}, safe=False)
    return JsonResponse({"error": "Invalid request"}, status=400)


def order_page(request):
    """
    Returns customer data (as JSON) by phone number from GET parameters.
    """
    if request.GET:
        user = get_user_by_phone(request.GET.get("phone_number", ""))
        return JsonResponse(user or {}, safe=False)
    return JsonResponse({"error": "Invalid request"}, status=400)


def index(request):
    """
    Renders the main page showing all categories and products.
    Handles displaying items stored in cookies (user's current order).
    """
    categories = Category.objects.all()
    products = Product.objects.all()
    orders = []
    orders_list = request.COOKIES.get("orders")
    total_price = request.COOKIES.get("total_price", 0)

    print("Orders list cookie:", orders_list)
    print("Total price cookie:", total_price)

    if orders_list:
        try:
            for key, val in json.loads(orders_list).items():
                product = Product.objects.filter(pk=int(key)).first()
                if product:
                    orders.append({
                        "product": product,
                        "count": val
                    })
        except json.JSONDecodeError:
            print("Invalid JSON in orders cookie")

    ctx = {
        "categories": categories,
        "products": products,
        "orders": orders,
        "total_price": total_price,
        "MEDIA_ROOT": MEDIA_ROOT
    }

    response = render(request, "products/index.html", ctx)
    response.set_cookie("greeting", "hello")
    return response


def main_order(request):
    """
    Handles order creation from the order page.
    Saves Customer, Order, and OrderProduct entries to the database.
    """
    model = Customer()

    if request.POST:
        try:
            # Try to get existing customer by phone number
            model = Customer.objects.get(phone_number=request.POST.get("phone_number", ""))
        except Customer.DoesNotExist:
            model = Customer()

        form = CustomerForm(request.POST or None, instance=model)
        if form.is_valid():
            customer = form.save()

            form_order = OrderForm(request.POST or None, instance=Order())
            if form_order.is_valid():
                order = form_order.save(customer=customer)
                print("order:", order)
                orders_list = request.COOKIES.get("orders")

                if orders_list:
                    try:
                        for key, value in json.loads(orders_list).items():
                            product = get_product_by_id(int(key))
                            if product:
                                order_product = OrderProduct(
                                    count=value,
                                    price=product["price"],
                                    product_id=product["id"],
                                    order_id=order.id
                                )
                                order_product.save()
                    except json.JSONDecodeError:
                        print("Invalid JSON in orders cookie")

                return redirect("index")
            else:
                print(form_order.errors)
        else:
            print(form.errors)

    # Prepare data for rendering if GET or invalid POST
    categories = Category.objects.all()
    products = Product.objects.all()
    orders = []
    orders_list = request.COOKIES.get("orders")
    total_price = request.COOKIES.get("total_price")

    if orders_list:
        try:
            for key, val in json.loads(orders_list).items():
                product = Product.objects.filter(pk=int(key)).first()
                if product:
                    orders.append({
                        "product": product,
                        "count": val
                    })
        except json.JSONDecodeError:
            print("Invalid JSON in orders cookie")

    ctx = {
        "categories": categories,
        "products": products,
        "orders": orders,
        "total_price": total_price,
        "MEDIA_ROOT": MEDIA_ROOT,
    }

    response = render(request, "products/order.html", ctx)
    response.set_cookie("greeting", "hello")
    return response