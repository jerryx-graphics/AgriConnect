# AgriConnect Backend

AgriConnect is a smart agricultural marketplace platform that connects farmers directly with buyers in Kenya's Kisii Region using AI and blockchain technology.

## 🚀 Current Implementation Status

### ✅ Completed Features

#### 1. Project Setup & Configuration
- Django 4.2+ with Django REST Framework
- Modular settings (development/production/testing)
- JWT authentication with refresh tokens
- PostgreSQL database configuration (with SQLite fallback for development)
- Redis caching and Celery task queue
- Environment variable management with python-decouple
- CORS configuration for frontend integration
- Comprehensive logging setup

#### 2. User Management System
- **Multi-role authentication** (Farmer, Buyer, Transporter, Cooperative, Admin)
- **Custom User model** with phone/email verification
- **Role-specific profiles**:
  - FarmerProfile (farm details, banking info, certifications)
  - BuyerProfile (business type, preferences)
  - TransporterProfile (vehicle details, service areas)
- **Authentication endpoints**:
  - User registration with role selection
  - Login with JWT tokens
  - Token refresh
  - Password change/reset
- **Verification system**:
  - Phone number verification (SMS ready)
  - Email verification with tokens
- **Profile management** with KYC support
- **Admin interface** with comprehensive user management

#### 3. Product Management System
- **Product models** with categories, images, and reviews
- **Advanced filtering** by location, price, quality, organic certification
- **Location-based search** with distance calculation
- **Product features**:
  - Multiple images per product
  - Price history tracking
  - Quality ratings and reviews
  - Inventory management
  - Analytics (views, inquiries, orders)
- **Wishlist functionality**
- **Search capabilities** with suggestions
- **Featured products** system
- **Admin interface** with inline editing

#### 4. Order Management System (Models Complete)
- **Complete order lifecycle** (pending → delivered → completed)
- **Shopping cart** functionality
- **Order tracking** with real-time updates
- **Delivery management** with transporter assignment
- **Invoice generation** system
- **Rating and feedback** system
- **Platform fee calculation** (3% default)

### 🚧 In Progress

#### Order Management Views & APIs
- Cart management endpoints
- Order creation and lifecycle management
- Order tracking and status updates
- Delivery request system

#### 6. API Documentation & Testing (✅ Completed)
- **Comprehensive Swagger/OpenAPI documentation** with interactive testing
- **Postman collection** with pre-configured requests and test scripts
- **Unit and integration tests** covering all core functionality
- **API testing guide** with examples and debugging tips
- **Security testing** for authentication and authorization

### 📋 Pending Implementation

#### 1. M-Pesa Payment Integration
- Daraja API integration
- Escrow payment system
- Payment webhooks
- Transaction management

#### 2. Blockchain Integration
- Smart contract integration
- Transaction recording on blockchain
- IPFS for product images
- QR code generation for traceability

#### 3. AI Services
- Price prediction models
- Demand forecasting
- Product recommendations
- Market insights

#### 4. Logistics & Delivery
- Route optimization
- GPS tracking integration
- Delivery cost calculation
- Transporter marketplace

#### 5. Notifications
- SMS notifications (Africa's Talking)
- Email notifications (SendGrid)
- Push notifications
- In-app messaging

## 🏗️ Architecture

### Core Apps Structure
```
agriconnect/
├── core/          # Shared utilities, base models, permissions
├── users/         # User management, authentication, profiles
├── products/      # Product catalog, categories, reviews
├── orders/        # Order management, cart, tracking
├── payments/      # M-Pesa integration, transactions
├── blockchain/    # Smart contracts, IPFS integration
├── ai_services/   # ML models, recommendations
├── logistics/     # Delivery management, routing
└── notifications/ # SMS, email, push notifications
```

### Key Features

#### Security
- JWT authentication with role-based permissions
- Input validation and sanitization
- CSRF and XSS protection
- Rate limiting on API endpoints
- Secure file upload validation
- Environment variable management

#### Performance
- Database query optimization with select_related/prefetch_related
- Redis caching for frequently accessed data
- Database indexes on critical fields
- Pagination for list endpoints
- Lazy loading where appropriate

#### Scalability
- Modular app structure
- Service layer pattern
- Async task processing with Celery
- Prepared for microservices architecture
- Clean separation of concerns

## 🔧 Installation & Setup

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Redis 6+
- Node.js (for frontend)

### Environment Variables
Copy `.env.example` to `.env` and configure:
```bash
cp .env.example .env
```

Key variables to set:
- `SECRET_KEY`: Django secret key
- `DB_*`: Database configuration
- `REDIS_URL`: Redis connection string
- `MPESA_*`: M-Pesa API credentials
- `AFRICASTALKING_*`: SMS API credentials
- `EMAIL_*`: Email service credentials

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver

# Start Celery worker (separate terminal)
celery -A agriconnect worker -l info
```

## 📊 Database Schema

### Core Models
- **User**: Custom user model with roles
- **UserProfile**: Basic profile information
- **FarmerProfile**: Farmer-specific data
- **BuyerProfile**: Buyer-specific data
- **TransporterProfile**: Transporter-specific data

### Product Models
- **ProductCategory**: Product categorization
- **Product**: Main product model with location/pricing
- **ProductImage**: Multiple images per product
- **ProductReview**: Customer reviews and ratings
- **Wishlist**: User wishlist functionality

### Order Models
- **Order**: Order management with status tracking
- **OrderItem**: Individual items in an order
- **Cart/CartItem**: Shopping cart functionality
- **OrderTracking**: Real-time order tracking
- **DeliveryRequest**: Delivery management
- **Invoice**: Invoice generation and tracking

## 📚 API Documentation

### 🔗 Interactive Documentation
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

### 📋 Postman Collection
Import `AgriConnect_API.postman_collection.json` for:
- Pre-configured API requests
- Authentication flow automation
- Test scripts and validation
- Environment variables setup

### 🔗 Key API Endpoints

#### Authentication & Users
- `POST /api/v1/auth/register/` - Multi-role user registration
- `POST /api/v1/auth/login/` - JWT token authentication
- `POST /api/v1/auth/token/refresh/` - Refresh access tokens
- `GET /api/v1/auth/profile/` - User profile management
- `POST /api/v1/auth/phone/send-verification/` - Phone verification
- `POST /api/v1/auth/email/send-verification/` - Email verification

#### Products & Catalog
- `GET /api/v1/products/` - Advanced product search & filtering
- `POST /api/v1/products/create/` - Create products (farmers only)
- `GET /api/v1/products/{id}/` - Detailed product information
- `GET /api/v1/products/categories/` - Product categories
- `GET /api/v1/products/featured/` - Featured products
- `POST /api/v1/products/{id}/reviews/` - Add product reviews
- `POST /api/v1/products/{id}/wishlist/add/` - Wishlist management

#### Orders & Shopping
- `GET /api/v1/orders/cart/` - Shopping cart management
- `POST /api/v1/orders/cart/add/` - Add items to cart
- `POST /api/v1/orders/create/` - Create orders from cart
- `GET /api/v1/orders/` - Order history and tracking
- `GET /api/v1/orders/{id}/` - Detailed order information
- `PUT /api/v1/orders/{id}/status/` - Update order status
- `POST /api/v1/orders/{id}/cancel/` - Cancel orders
- `POST /api/v1/orders/{id}/rate/` - Rate completed orders

#### Advanced Features
- Location-based product search
- Real-time order tracking
- Multi-role access control
- File upload for product images
- Price history tracking
- Analytics and insights

## 🧪 Testing

### Unit & Integration Tests
```bash
# Run all tests
python manage.py test

# Run with coverage
pytest --cov=. tests/

# Run specific test suites
python manage.py test tests.test_api_endpoints.AuthenticationAPITests
python manage.py test tests.test_api_endpoints.ProductAPITests
python manage.py test tests.test_api_endpoints.OrderAPITests

# Run app-specific tests
python manage.py test users
python manage.py test products
python manage.py test orders
```

### API Testing
```bash
# Interactive testing via Swagger UI
open http://localhost:8000/api/docs/

# Import Postman collection
# File: AgriConnect_API.postman_collection.json

# Manual API testing examples
curl -X POST "http://localhost:8000/api/v1/auth/register/" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","role":"farmer",...}'
```

### Test Coverage
- **Authentication**: Registration, login, JWT tokens, role-based access
- **Products**: CRUD operations, search, filtering, reviews
- **Orders**: Cart management, order creation, tracking, status updates
- **Security**: Authorization, input validation, rate limiting
- **Documentation**: API endpoints accessibility and functionality

## 📱 Mobile App Support

The API is designed to support mobile applications with:
- Optimized JSON responses
- Image optimization and CDN support
- Offline-capable design patterns
- Push notification support
- Location-based services

## 🌍 Localization

Prepared for multi-language support:
- English (default)
- Kiswahili
- Ekegusii (local Kisii language)

## 🚀 Deployment

### Production Checklist
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] Static files collected
- [ ] HTTPS configured
- [ ] Monitoring setup
- [ ] Backup strategy implemented

### Docker Support (Planned)
- Docker compose for development
- Production-ready Dockerfile
- Environment-specific configurations

## 📈 Analytics & Monitoring

Built-in analytics for:
- Product views and engagement
- Order patterns and trends
- User behavior tracking
- Revenue analytics
- Performance monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is proprietary software for AgriConnect Kenya.

## 📞 Support

For technical support or questions:
- Email: tech@agriconnect.co.ke
- Documentation: [Coming Soon]
- API Docs: http://localhost:8000/api/docs/