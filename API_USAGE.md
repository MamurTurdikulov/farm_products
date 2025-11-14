# API Usage Examples

## Obtain JWT token
Request:
```
POST /api/token/
Content-Type: application/json

{"username":"admin","password":"password123"}
```
Response:
```
{"access":"<ACCESS_TOKEN>","refresh":"<REFRESH_TOKEN>"}
```

## Refresh token
Request:
```
POST /api/token/refresh/
{"refresh":"<REFRESH_TOKEN>"}
```

## List products (public)
```
GET /api/products/
```
Supports pagination (`?page=2`), search (`?search=apple`), and filtering by category (`?category=1`).

## Create a customer (authenticated or anonymous via API)
```
POST /api/customers/
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json

{"name":"John","surname":"Doe","phone":"+998901234567","email":"john@example.com"}
```

## Create an order (authenticated)
```
POST /api/orders/
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json

{
  "customer_id": 1,
  "product_id": 2,
  "kilos_ordered": 3.5,
  "note": "Please deliver on Monday"
}
```

If product stock is insufficient, the API will return HTTP 400 with `{"detail":"Not enough stock available."}`.