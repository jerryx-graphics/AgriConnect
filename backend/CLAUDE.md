# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AgriConnect is a smart agricultural marketplace platform connecting farmers directly with buyers in Kenya's Kisii Region using AI and blockchain technology. This is a Django REST Framework backend with a modular architecture supporting multiple user roles (Farmer, Buyer, Transporter, Cooperative, Admin).

## Development Commands

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment variables template
cp .env.example .env
# Edit .env with your configuration

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver

# Start Celery worker (separate terminal)
celery -A agriconnect worker -l info
```

### Testing
```bash
# Run all tests
python manage.py test

# Run with coverage
pytest --cov=. tests/

# Run specific test modules
python manage.py test tests.test_api_endpoints.AuthenticationAPITests
python manage.py test tests.test_api_endpoints.ProductAPITests
python manage.py test tests.test_api_endpoints.OrderAPITests

# Run app-specific tests
python manage.py test users
python manage.py test products
python manage.py test orders
```

### Database Management
```bash
# Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# Reset database (if needed)
python manage.py flush

# Load sample data (if fixtures exist)
python manage.py loaddata fixtures/sample_data.json
```

### Production Commands
```bash
# Collect static files
python manage.py collectstatic --noinput

# Run with Gunicorn
gunicorn --bind 0.0.0.0:8000 --workers 3 agriconnect.wsgi:application
```

## Architecture Overview

### App Structure
- **core/**: Shared utilities, base models, permissions
- **users/**: Multi-role authentication system with custom User model
- **products/**: Product catalog with location-based search and reviews
- **orders/**: Complete order management with cart and tracking
- **payments/**: M-Pesa integration (planned)
- **blockchain/**: Smart contract integration (planned)
- **ai_services/**: ML models and recommendations (planned)
- **logistics/**: Delivery and route optimization (planned)
- **notifications/**: SMS/email/push notifications (planned)

### Key Design Patterns
- **Multi-role authentication** with custom User model and role-specific profiles
- **Service layer pattern** for complex business logic
- **Django REST Framework** with comprehensive serializers and viewsets
- **JWT authentication** with refresh token rotation
- **Location-based services** using latitude/longitude coordinates
- **Comprehensive API documentation** with Swagger/OpenAPI

### Database Models
- Custom User model with roles: FARMER, BUYER, TRANSPORTER, COOPERATIVE, ADMIN
- Role-specific profiles: FarmerProfile, BuyerProfile, TransporterProfile
- Product catalog with categories, images, reviews, and location data
- Order management with cart, tracking, and delivery system
- Built-in analytics tracking for products and orders

### Settings Configuration
- **Modular settings** in `agriconnect/settings/` (base, development, production)
- **Environment variables** managed with python-decouple
- **Database**: PostgreSQL (with SQLite fallback for development)
- **Caching**: Redis with django-redis
- **Task queue**: Celery with Redis broker
- **File storage**: Local (with S3 support via USE_S3 flag)

## API Documentation

### Interactive Documentation
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- OpenAPI Schema: http://localhost:8000/api/schema/

### Authentication Flow
1. Register user: `POST /api/v1/auth/register/`
2. Login: `POST /api/v1/auth/login/` (returns JWT tokens)
3. Use Bearer token in Authorization header
4. Refresh token: `POST /api/v1/auth/token/refresh/`

### Key Endpoints
- **Auth**: `/api/v1/auth/` - Registration, login, profile management
- **Products**: `/api/v1/products/` - Catalog, search, reviews, wishlist
- **Orders**: `/api/v1/orders/` - Cart, order management, tracking
- **Admin**: `/admin/` - Django admin interface

## Development Guidelines

### Code Style
- Follow Django and DRF best practices
- Use the existing serializer patterns for new endpoints
- Implement proper error handling with descriptive messages
- Add appropriate permissions to all viewsets
- Use select_related/prefetch_related for query optimization

### Security
- All API endpoints require authentication by default
- Role-based permissions implemented via custom permission classes
- Input validation through serializers
- File upload validation for images
- Rate limiting configured on sensitive endpoints

### Testing
- Write tests for all new functionality
- Use the existing test patterns in `tests/test_api_endpoints.py`
- Test authentication, authorization, and business logic
- Mock external services (M-Pesa, blockchain, etc.)

### Docker Support
- Dockerfile provided for containerization
- docker-compose.yml and docker-compose.prod.yml available
- Environment configured for both development and production

## Environment Variables

Copy `.env.example` to `.env` and configure:

### Required for Development
- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to True for development
- `DB_*`: Database configuration (defaults to local PostgreSQL)
- `REDIS_URL`: Redis connection string

### External Services (Optional)
- `MPESA_*`: M-Pesa Daraja API credentials
- `AFRICASTALKING_*`: SMS service credentials
- `EMAIL_*`: Email service credentials (SendGrid)
- `WEB3_*`: Blockchain configuration
- `AWS_*`: S3 file storage (if USE_S3=True)

## Common Issues

### Database Setup
- Ensure PostgreSQL is running and database exists
- Run migrations after model changes
- Use SQLite for quick development by modifying DATABASE setting

### Celery Tasks
- Ensure Redis is running for Celery broker
- Start Celery worker in separate terminal
- Check Celery logs for task execution issues

### Authentication Issues
- JWT tokens expire after 1 hour (configurable in settings)
- Use refresh tokens to get new access tokens
- Check token format: `Bearer <access_token>`

### File Uploads
- Media files stored in `/media/` directory in development
- Configure S3 for production file storage
- Image validation implemented for product images