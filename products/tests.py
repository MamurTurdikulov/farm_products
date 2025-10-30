from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from .models import Category, Product, Customer, Order, OrderProduct
from .services import get_product_by_id, get_user_by_phone

class CategoryModelTest(TestCase):
    def test_create_category(self):
        category = Category.objects.create(title="Vegetables")
        self.assertEqual(str(category), "Vegetables")
        self.assertIsNotNone(category.created_at)

class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(title="Fruits")

    def test_create_product(self):
        product = Product.objects.create(
            title="Apple",
            description="Fresh red apple",
            category=self.category,
            cost=5000,
            price=7000,
            image="products/apple.jpg",
        )
        self.assertEqual(str(product), "Apple")
        self.assertEqual(product.category.title, "Fruits")

class CustomerModelTest(TestCase):
    def test_create_customer(self):
        customer = Customer.objects.create(
            first_name="John",
            last_name="Doe",
            phone_number="+998901112233",
        )
        self.assertEqual(str(customer), "John Doe")
        self.assertIsNotNone(customer.created_at)

class OrderModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="Alice",
            last_name="Smith",
            phone_number="+998901234567",
        )

    def test_create_order(self):
        order = Order.objects.create(
            payment_type=1,
            status=1,
            address="Farm Street 123",
            customer=self.customer,
        )
        self.assertEqual(order.customer.first_name, "Alice")
        self.assertEqual(order.status, 1)

class OrderProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(title="Fruits")
        self.product = Product.objects.create(
            title="Banana",
            description="Yellow banana",
            category=self.category,
            cost=2000,
            price=3000,
            image="products/banana.jpg",
        )
        self.customer = Customer.objects.create(
            first_name="Bob",
            last_name="Brown",
            phone_number="+998909999999",
        )
        self.order = Order.objects.create(
            payment_type=1,
            status=1,
            address="Green Valley",
            customer=self.customer,
        )

    def test_create_order_product(self):
        order_product = OrderProduct.objects.create(
            count=3,
            price=self.product.price,
            product=self.product,
            order=self.order,
        )
        self.assertEqual(order_product.count, 3)
        self.assertEqual(order_product.order.customer.phone_number, "+998909999999")

class ServicesTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(title="Grains")
        self.product = Product.objects.create(
            title="Wheat",
            description="Organic wheat",
            category=self.category,
            cost=4000,
            price=6000,
            image="products/wheat.jpg",
        )
        self.customer = Customer.objects.create(
            first_name="Eve",
            last_name="Walker",
            phone_number="+998901010101",
        )

    def test_get_product_by_id(self):
        product_data = get_product_by_id(self.product.id)
        self.assertIsInstance(product_data, dict)
        self.assertEqual(product_data["title"], "Wheat")

    def test_get_user_by_phone(self):
        user_data = get_user_by_phone(self.customer.phone_number)
        self.assertIsInstance(user_data, dict)
        self.assertEqual(user_data["phone_number"], "+998901010101")

class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(title="Vegetables")
        self.product = Product.objects.create(
            title="Tomato",
            description="Fresh tomato",
            category=self.category,
            cost=3000,
            price=5000,
            image="products/tomato.jpg",
        )

    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tomato")

    def test_home_page_json(self):
        response = self.client.get(reverse('home_page'), {"product_id": self.product.id})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["title"], "Tomato")