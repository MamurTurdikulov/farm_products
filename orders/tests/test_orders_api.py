from rest_framework.test import APITestCase
from users.models import User
from products.models import Product
from rest_framework import status

class OrderAPITest(APITestCase):

    def setUp(self):
        self.buyer = User.objects.create_user(
            username="buyer",
            password="1234",
            role="buyer"
        )
        self.seller = User.objects.create_user(
            username="seller",
            password="1234",
            role="seller"
        )
        self.product = Product.objects.create(
            name="Banana",
            price=7
        )

    def authenticate(self, user):
        response = self.client.post(
            "/api/auth/login/",
            {"username": user.username, "password": "1234"}
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {response.data['access']}"
        )

    def test_buyer_can_order(self):
        self.authenticate(self.buyer)
        response = self.client.post("/api/orders/", {
            "product": self.product.id,
            "quantity": 2
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_seller_cannot_order(self):
        self.authenticate(self.seller)
        response = self.client.post("/api/orders/", {
            "product": self.product.id,
            "quantity": 1
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)