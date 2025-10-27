# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AgriConnect is a full-stack agricultural marketplace platform connecting farmers directly with buyers in Kenya's Kisii Region. The project consists of a Django REST Framework backend with blockchain/AI capabilities and a Next.js frontend with modern UI components.

## Development Commands

### Backend (Django)
```bash
# Setup and dependencies
cd backend
pip install -r requirements.txt
cp .env.example .env  # Configure environment variables

# Database operations
python manage.py migrate
python manage.py createsuperuser

# Development server
python manage.py runserver

# Background tasks
celery -A agriconnect worker -l info

# Testing
python manage.py test
pytest --cov=. tests/
python manage.py test users products orders  # App-specific tests
```

### Frontend (Next.js)
```bash
# Setup and dependencies
cd frontend
npm install

# Development
npm run dev        # Start development server
npm run build      # Build for production
npm run start      # Start production server
npm run lint       # Run ESLint
```

## Architecture Overview

### Backend Structure
- **Django REST Framework** with modular app architecture
- **Multi-role authentication** system (Farmer, Buyer, Transporter, Cooperative, Admin)
- **Location-based services** with coordinate-based product search
- **JWT authentication** with refresh token rotation
- **Service layer pattern** for complex business logic
- **Celery task queue** with Redis broker for async operations

#### Key Backend Apps
- `users/`: Multi-role user system with custom profiles
- `products/`: Product catalog with location search, reviews, analytics
- `orders/`: Complete order lifecycle with cart, tracking, delivery
- `payments/`: M-Pesa integration (planned)
- `blockchain/`: Smart contract integration (planned)
- `ai_services/`: ML recommendations and price prediction (planned)
- `logistics/`: Route optimization and delivery management (planned)
- `notifications/`: Multi-channel notification system (planned)

### Frontend Structure
- **Next.js 16** with App Router
- **TypeScript** configuration with build error tolerance
- **Tailwind CSS** with custom design system
- **Radix UI** components for accessibility
- **React Hook Form** with Zod validation
- **Recharts** for data visualization

#### Key Frontend Features
- Modern component architecture with shadcn/ui
- Responsive design with mobile-first approach
- Dark mode support via next-themes
- Form validation and state management
- Data visualization components

## API Documentation

### Interactive Docs
- Swagger UI: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`
- OpenAPI Schema: `http://localhost:8000/api/schema/`
- Postman Collection: `backend/AgriConnect_API.postman_collection.json`

### Authentication Flow
1. Register: `POST /api/v1/auth/register/` with role selection
2. Login: `POST /api/v1/auth/login/` (returns JWT tokens)
3. Use Bearer token in Authorization header
4. Refresh: `POST /api/v1/auth/token/refresh/`

### Key API Endpoints
- **Auth**: `/api/v1/auth/` - Registration, login, profile management
- **Products**: `/api/v1/products/` - Catalog, search, reviews, wishlist
- **Orders**: `/api/v1/orders/` - Cart, order management, tracking

## Database Configuration

### Development
- PostgreSQL (primary) with SQLite fallback
- Redis for caching and Celery broker
- Migrations in `backend/*/migrations/`

### Key Models
- Custom User model with role-based profiles
- Location-aware Product model with coordinates
- Complete Order lifecycle with tracking
- Analytics integration across all models

## Environment Setup

### Backend Environment Variables
Copy `backend/.env.example` to `backend/.env` and configure:
- `SECRET_KEY`, `DEBUG`, `DB_*` (required)
- `REDIS_URL` for caching and Celery
- `MPESA_*`, `AFRICASTALKING_*`, `EMAIL_*` (external services)

### Frontend Configuration
- Next.js config in `frontend/next.config.mjs`
- TypeScript build errors ignored for development
- Image optimization disabled for flexibility

## Testing Strategy

### Backend Testing
- Comprehensive test suite in `backend/tests/`
- API endpoint testing with authentication flows
- Model validation and business logic testing
- Role-based permission testing

### Test Commands
```bash
# Backend testing
python manage.py test tests.test_api_endpoints.AuthenticationAPITests
python manage.py test tests.test_api_endpoints.ProductAPITests
python manage.py test tests.test_api_endpoints.OrderAPITests
```

## Development Guidelines

### Code Patterns
- Follow existing Django/DRF patterns in backend
- Use shadcn/ui component patterns in frontend
- Implement proper error handling with descriptive messages
- Role-based permissions on all sensitive endpoints
- Query optimization with select_related/prefetch_related

### Security Considerations
- JWT authentication required by default
- Input validation through serializers
- File upload validation for images
- Rate limiting on sensitive endpoints
- Environment variable management for secrets

## Common Issues

### Backend
- Ensure PostgreSQL and Redis are running
- Run migrations after model changes
- Check Celery worker for background tasks
- JWT tokens expire after 1 hour (configurable)

### Frontend
- TypeScript build errors are ignored in development
- Use absolute imports from project root
- Follow Tailwind CSS conventions
- Ensure proper Next.js App Router usage