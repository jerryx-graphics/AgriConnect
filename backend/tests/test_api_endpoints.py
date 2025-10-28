"""
Comprehensive API endpoint tests for AgriConnect
"""
import json
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from products.models import ProductCategory, Product
from orders.models import Cart, CartItem, Order

User = get_user_model()


class AuthenticationAPITests(APITestCase):
    """Test authentication endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.registration_url = reverse('user-register')
        self.login_url = reverse('user-login')

    def test_user_registration_farmer(self):
        """Test farmer registration"""
        data = {
            'email': 'farmer@test.com',
            'username': 'testfarmer',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'Farmer',
            'phone_number': '+254712345678',
            'role': 'farmer'
        }
        response = self.client.post(self.registration_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['user']['role'], 'farmer')
        self.assertIn('tokens', response.data['data'])

    def test_user_registration_buyer(self):
        """Test buyer registration"""
        data = {
            'email': 'buyer@test.com',
            'username': 'testbuyer',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'Buyer',
            'phone_number': '+254712345679',
            'role': 'buyer'
        }
        response = self.client.post(self.registration_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['data']['user']['role'], 'buyer')

    def test_user_login(self):
        """Test user login"""
        # Create user first
        user = User.objects.create_user(
            email='test@test.com',
            username='testuser',
            password='TestPass123!',
            first_name='Test',
            last_name='User',
            phone_number='+254712345678',
            role='farmer'
        )

        data = {
            'email': 'test@test.com',
            'password': 'TestPass123!'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('tokens', response.data['data'])

    def test_invalid_login(self):
        """Test login with invalid credentials"""
        data = {
            'email': 'invalid@test.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])


class ProductAPITests(APITestCase):
    """Test product endpoints"""

    def setUp(self):
        self.client = APIClient()

        # Create test users
        self.farmer = User.objects.create_user(
            email='farmer@test.com',
            username='farmer',
            password='TestPass123!',
            role='farmer',
            first_name='Test',
            last_name='Farmer',
            phone_number='+254712345678'
        )

        self.buyer = User.objects.create_user(
            email='buyer@test.com',
            username='buyer',
            password='TestPass123!',
            role='buyer',
            first_name='Test',
            last_name='Buyer',
            phone_number='+254712345679'
        )

        # Create test category
        self.category = ProductCategory.objects.create(
            name='Fruits',
            description='Fresh fruits'
        )

        # URLs
        self.products_url = reverse('product-list')
        self.create_product_url = reverse('product-create')

    def test_list_products_public(self):
        """Test public access to product list"""
        response = self.client.get(self.products_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_product_as_farmer(self):
        """Test creating product as farmer"""
        self.client.force_authenticate(user=self.farmer)

        data = {
            'name': 'Fresh Bananas',
            'description': 'Sweet ripe bananas',
            'category': self.category.id,
            'price_per_unit': '150.00',
            'unit': 'kg',
            'quantity_available': '100.00',
            'minimum_order': '5.00',
            'condition': 'fresh',
            'quality_grade': 'premium',
            'county': 'Kisii',
            'is_organic': True
        }

        response = self.client.post(self.create_product_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['name'], 'Fresh Bananas')

    def test_create_product_as_buyer_forbidden(self):
        """Test that buyers cannot create products"""
        self.client.force_authenticate(user=self.buyer)

        data = {
            'name': 'Test Product',
            'description': 'Test',
            'category': self.category.id,
            'price_per_unit': '100.00',
            'unit': 'kg',
            'quantity_available': '50.00'
        }

        response = self.client.post(self.create_product_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_products_by_county(self):
        """Test filtering products by county"""
        # Create test product
        Product.objects.create(
            farmer=self.farmer,
            category=self.category,
            name='Test Product',
            description='Test',
            price_per_unit=100.00,
            quantity_available=50.00,
            county='Kisii'
        )

        response = self.client.get(self.products_url, {'county': 'Kisii'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_search_products(self):
        """Test product search functionality"""
        Product.objects.create(
            farmer=self.farmer,
            category=self.category,
            name='Fresh Bananas',
            description='Sweet ripe bananas',
            price_per_unit=150.00,
            quantity_available=100.00,
            county='Kisii'
        )

        response = self.client.get(self.products_url, {'search': 'banana'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class OrderAPITests(APITestCase):
    """Test order and cart endpoints"""

    def setUp(self):
        self.client = APIClient()

        # Create test users
        self.farmer = User.objects.create_user(
            email='farmer@test.com',
            username='farmer',
            password='TestPass123!',
            role='farmer',
            first_name='Test',
            last_name='Farmer',
            phone_number='+254712345678'
        )

        self.buyer = User.objects.create_user(
            email='buyer@test.com',
            username='buyer',
            password='TestPass123!',
            role='buyer',
            first_name='Test',
            last_name='Buyer',
            phone_number='+254712345679'
        )

        # Create test product
        self.category = ProductCategory.objects.create(name='Fruits')
        self.product = Product.objects.create(
            farmer=self.farmer,
            category=self.category,
            name='Test Bananas',
            description='Fresh bananas',
            price_per_unit=150.00,
            quantity_available=100.00,
            minimum_order=5.00,
            county='Kisii'
        )

        # URLs
        self.cart_url = reverse('cart')
        self.add_to_cart_url = reverse('add-to-cart')
        self.orders_url = reverse('order-list')
        self.create_order_url = reverse('order-create')

    def test_view_cart_authenticated(self):
        """Test viewing cart as authenticated user"""
        self.client.force_authenticate(user=self.buyer)
        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_to_cart(self):
        """Test adding item to cart"""
        self.client.force_authenticate(user=self.buyer)

        data = {
            'product_id': str(self.product.id),
            'quantity': 10.0
        }

        response = self.client.post(self.add_to_cart_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])

    def test_create_order(self):
        """Test creating an order from cart items"""
        self.client.force_authenticate(user=self.buyer)

        data = {
            'delivery_address': '123 Test Street',
            'delivery_county': 'Kisii',
            'delivery_phone': '+254712345679',
            'cart_items': [
                {
                    'product_id': str(self.product.id),
                    'quantity': 10.0,
                    'special_instructions': 'Handle with care'
                }
            ]
        }

        response = self.client.post(self.create_order_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['status'], 'pending')

    def test_list_orders(self):
        """Test listing user orders"""
        self.client.force_authenticate(user=self.buyer)

        # Create test order
        order = Order.objects.create(
            buyer=self.buyer,
            delivery_address='Test Address',
            delivery_county='Kisii',
            delivery_phone='+254712345679'
        )

        response = self.client.get(self.orders_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class APIDocumentationTests(TestCase):
    """Test API documentation endpoints"""

    def setUp(self):
        self.client = APIClient()

    def test_swagger_ui_accessible(self):
        """Test that Swagger UI is accessible"""
        response = self.client.get('/api/docs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_redoc_accessible(self):
        """Test that ReDoc is accessible"""
        response = self.client.get('/api/redoc/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_openapi_schema_accessible(self):
        """Test that OpenAPI schema is accessible"""
        response = self.client.get('/api/schema/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['content-type'], 'application/vnd.oai.openapi')


class APISecurityTests(APITestCase):
    """Test API security measures"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@test.com',
            username='testuser',
            password='TestPass123!',
            role='farmer'
        )

    def test_authentication_required_for_protected_endpoints(self):
        """Test that protected endpoints require authentication"""
        protected_urls = [
            reverse('user-profile'),
            reverse('product-create'),
            reverse('cart'),
            reverse('order-list')
        ]

        for url in protected_urls:
            response = self.client.get(url)
            self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_jwt_token_authentication(self):
        """Test JWT token authentication"""
        # Login to get token
        login_data = {
            'email': 'test@test.com',
            'password': 'TestPass123!'
        }
        response = self.client.post(reverse('user-login'), login_data, format='json')
        token = response.data['data']['tokens']['access']

        # Use token to access protected endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(reverse('user-profile'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_token_rejected(self):
        """Test that invalid tokens are rejected"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid-token')
        response = self.client.get(reverse('user-profile'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)