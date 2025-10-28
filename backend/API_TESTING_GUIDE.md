# AgriConnect API Testing Guide

## 🔗 API Documentation

The AgriConnect API is fully documented and can be tested through multiple interfaces:

### 📚 Interactive Documentation
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

### 📋 Postman Collection
Import the provided Postman collection for comprehensive API testing:
- File: `AgriConnect_API.postman_collection.json`
- Pre-configured with variables and test scripts
- Includes authentication flow and sample requests

## 🚀 Quick Start Testing

### 1. Start the Development Server
```bash
./deploy.sh development
```

### 2. Access API Documentation
Visit http://localhost:8000/api/docs/ to see the interactive Swagger UI with:
- All endpoints documented
- Request/response examples
- Authentication setup
- Try-it-out functionality

### 3. Test Authentication Flow

#### Register a Farmer
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "farmer@example.com",
    "username": "farmer1",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+254712345678",
    "role": "farmer"
  }'
```

#### Login and Get Tokens
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "farmer@example.com",
    "password": "SecurePass123!"
  }'
```

#### Use Token for Authenticated Requests
```bash
curl -X GET "http://localhost:8000/api/v1/auth/profile/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 📊 API Endpoints Overview

### Authentication Endpoints
- `POST /api/v1/auth/register/` - User registration
- `POST /api/v1/auth/login/` - User login
- `POST /api/v1/auth/token/refresh/` - Refresh JWT token
- `GET /api/v1/auth/profile/` - Get user profile
- `PUT /api/v1/auth/profile/` - Update user profile

### Product Endpoints
- `GET /api/v1/products/` - List products (with filtering)
- `POST /api/v1/products/create/` - Create product (farmers only)
- `GET /api/v1/products/{id}/` - Product details
- `PUT /api/v1/products/{id}/update/` - Update product
- `GET /api/v1/products/categories/` - Product categories
- `GET /api/v1/products/featured/` - Featured products

### Order & Cart Endpoints
- `GET /api/v1/orders/cart/` - View cart
- `POST /api/v1/orders/cart/add/` - Add to cart
- `POST /api/v1/orders/create/` - Create order
- `GET /api/v1/orders/` - List orders
- `GET /api/v1/orders/{id}/` - Order details
- `PUT /api/v1/orders/{id}/status/` - Update order status

## 🧪 Running Tests

### Unit Tests
```bash
# Run all tests
python manage.py test

# Run specific test class
python manage.py test tests.test_api_endpoints.AuthenticationAPITests

# Run with coverage
pytest --cov=. tests/
```

### API Integration Tests
```bash
# Test authentication endpoints
python manage.py test tests.test_api_endpoints.AuthenticationAPITests

# Test product endpoints
python manage.py test tests.test_api_endpoints.ProductAPITests

# Test order endpoints
python manage.py test tests.test_api_endpoints.OrderAPITests

# Test API documentation
python manage.py test tests.test_api_endpoints.APIDocumentationTests

# Test security
python manage.py test tests.test_api_endpoints.APISecurityTests
```

## 📝 Testing Scenarios

### Complete User Journey Test

#### 1. Farmer Registration & Product Creation
```bash
# 1. Register farmer
POST /api/v1/auth/register/
{
  "email": "farmer@test.com",
  "role": "farmer",
  ...
}

# 2. Login and get tokens
POST /api/v1/auth/login/

# 3. Create product
POST /api/v1/products/create/
{
  "name": "Fresh Bananas",
  "price_per_unit": "150.00",
  ...
}
```

#### 2. Buyer Shopping Flow
```bash
# 1. Register buyer
POST /api/v1/auth/register/
{
  "role": "buyer",
  ...
}

# 2. Browse products
GET /api/v1/products/?county=Kisii&is_organic=true

# 3. Add to cart
POST /api/v1/orders/cart/add/
{
  "product_id": "uuid",
  "quantity": 10
}

# 4. Create order
POST /api/v1/orders/create/
{
  "delivery_address": "123 Main St",
  "cart_items": [...]
}
```

#### 3. Order Management
```bash
# 1. Farmer confirms order
PUT /api/v1/orders/{id}/status/
{
  "status": "confirmed",
  "message": "Order confirmed"
}

# 2. Track order progress
GET /api/v1/orders/{id}/

# 3. Complete order
PUT /api/v1/orders/{id}/status/
{
  "status": "delivered"
}
```

## 🔒 Security Testing

### Authentication Tests
- Test JWT token validation
- Test role-based access control
- Test token expiration and refresh
- Test invalid credential handling

### Authorization Tests
- Verify farmers can only edit their products
- Verify buyers can only see their orders
- Test admin access to all resources
- Test transporter access to delivery requests

### Input Validation Tests
- Test SQL injection prevention
- Test XSS protection
- Test file upload validation
- Test rate limiting

## 📊 Performance Testing

### Load Testing with Artillery
```bash
# Install Artillery
npm install -g artillery

# Create load test config
artillery quick --count 100 --num 10 http://localhost:8000/api/v1/products/

# Test authentication endpoints
artillery quick --count 50 --num 5 http://localhost:8000/api/v1/auth/login/
```

### Database Query Optimization
```bash
# Enable query debugging
export DEBUG_QUERIES=True

# Monitor slow queries
python manage.py shell
>>> from django.db import connection
>>> print(connection.queries)
```

## 🔍 Debugging API Issues

### Common Issues and Solutions

#### 1. Authentication Errors
```bash
# Check token format
Authorization: Bearer <token>

# Verify token hasn't expired
# Check user permissions for endpoint
```

#### 2. Validation Errors
```bash
# Check required fields in request
# Verify data types match serializer
# Check foreign key relationships
```

#### 3. Permission Denied
```bash
# Verify user role matches endpoint requirements
# Check object-level permissions
# Ensure user is authenticated
```

### Debug Tools
```bash
# Enable Django debug mode
DEBUG=True

# Use Django Debug Toolbar
pip install django-debug-toolbar

# Log API requests
LOGGING_LEVEL=DEBUG
```

## 📈 API Monitoring

### Health Checks
```bash
# Check API health
curl http://localhost:8000/api/v1/products/

# Check database connectivity
python manage.py check --database default

# Check Redis connectivity
redis-cli ping
```

### Performance Metrics
- Response time monitoring
- Error rate tracking
- Database query performance
- Cache hit rates

## 🎯 Test Data Setup

### Create Test Users
```python
# In Django shell
python manage.py shell

from users.models import User
farmer = User.objects.create_user(
    email='farmer@test.com',
    username='farmer',
    password='test123',
    role='farmer'
)
```

### Create Test Products
```python
from products.models import ProductCategory, Product

category = ProductCategory.objects.create(name='Fruits')
product = Product.objects.create(
    farmer=farmer,
    category=category,
    name='Test Bananas',
    price_per_unit=150.00,
    quantity_available=100.00
)
```

## 📞 Support

For API testing issues:
- Check the interactive documentation first
- Review the test suite for examples
- Check logs for detailed error messages
- Contact: tech@agriconnect.co.ke

## 🔄 Continuous Testing

### CI/CD Integration
```yaml
# GitHub Actions example
- name: Run API Tests
  run: |
    python manage.py test
    python manage.py check --deploy
```

### Pre-commit Testing
```bash
# Install pre-commit hooks
pre-commit install

# Run tests before commit
python manage.py test
flake8 .
black .
```