from django.test import TestCase
from rest_framework.test import APIClient
from .models import Category, Product, Customer, Order


class APITest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create test category
        self.category = Category.objects.create(
            name='Fruits',
            description='Fresh fruits'
        )

        # Create test products
        self.product1 = Product.objects.create(
            name='Apple',
            description='Red apple',
            price=100,
            quantity=50,
            category=self.category
        )
        self.product2 = Product.objects.create(
            name='Banana',
            description='Yellow banana',
            price=50,
            quantity=100,
            category=self.category
        )

        # Create test customer
        self.customer = Customer.objects.create(
            name='John Doe',
            email='john@example.com',
            phone='+1234567890',
            address='Farm Street 1'
        )

    def _extract_results(self, response):
        """
        Helper to handle both paginated and non-paginated responses.
        """
        data = response.json()
        if isinstance(data, dict) and "results" in data:
            return data["results"]
        return data

    def test_list_products(self):
        """Ensure we can list products via API."""
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, 200)

        data = self._extract_results(response)
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 2)
        self.assertTrue(any(p["name"] == "Apple" for p in data))

    def test_search_products(self):
        """Ensure searching products by name works."""
        response = self.client.get('/api/products/?search=Apple')
        self.assertEqual(response.status_code, 200)

        data = self._extract_results(response)
        self.assertTrue(any('Apple' in p['name'] for p in data))

    def test_create_customer(self):
        """Ensure creating a customer via API works."""
        payload = {
            'name': 'Alice Smith',
            'email': 'alice@example.com',
            'phone': '+998901234567',
            'address': 'Tashkent'
        }
        response = self.client.post('/api/customers/', payload, format='json')
        self.assertIn(response.status_code, [200, 201], msg=response.content)

        # Verify new customer exists in DB
        self.assertTrue(Customer.objects.filter(email='alice@example.com').exists())

    def test_create_order(self):
        """Ensure creating an order via API works."""
        payload = {
            'customer': self.customer.id,
            'product': self.product1.id,
            'kilos': 3,
            'status': 'Pending'
        }
        response = self.client.post('/api/orders/', payload, format='json')
        self.assertIn(response.status_code, [200, 201], msg=response.content)

        # Verify new order was created correctly
        order = Order.objects.last()
        self.assertEqual(order.customer, self.customer)
        self.assertEqual(order.product, self.product1)
        self.assertEqual(order.quantity, 3)
        self.assertEqual(float(order.total_price), float(self.product1.price * 3))
        # Stock must decrease
        self.product1.refresh_from_db()
        self.assertEqual(self.product1.quantity, 47)
