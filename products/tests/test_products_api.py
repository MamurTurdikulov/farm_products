from rest_framework.test import APITestCase
from django.urls import reverse
from users.models import User
from rest_framework import status

class ProductAPITest(APITestCase):

    def setUp(self):
        self.seller = User.objects.create_user(
            username="seller",
            password="1234",
            role="seller"
        )
        self.buyer = User.objects.create_user(
            username="buyer",
            password="1234",
            role="buyer"
        )

        self.product_url = reverse("product-list")

    def authenticate(self, user):
        response = self.client.post(
            "/api/auth/login/",
            {"username": user.username, "password": "1234"}
        )
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_seller_can_create_product(self):
        self.authenticate(self.seller)
        response = self.client.post(self.product_url, {
            "name": "Apple",
            "price": 10
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_buyer_cannot_create_product(self):
        self.authenticate(self.buyer)
        response = self.client.post(self.product_url, {
            "name": "Orange",
            "price": 5
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)