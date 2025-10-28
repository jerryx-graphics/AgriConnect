# AgriConnect

AgriConnect is a comprehensive agricultural marketplace platform designed to connect farmers, buyers, transporters, and cooperatives in Kenya's Kisii Region. By leveraging AI and blockchain, AgriConnect streamlines agricultural trade, logistics, payments, and provides data-driven insights for all stakeholders.

---

## 🏗️ Project Structure
```
AgriConnect/
├── backend/   # Django REST API, business logic, AI & blockchain integrations
├── frontend/  # Next.js web app for all user roles
```
- **backend/**: Contains all server-side code, including user management, product catalog, orders, payments, logistics, notifications, and integrations with AI and blockchain services.
- **frontend/**: Contains the web application for farmers, buyers, transporters, cooperatives, and admins, built with Next.js and TypeScript.

---

## 🚀 Key Features
### User Management
- Multi-role authentication (Farmer, Buyer, Transporter, Cooperative, Admin)
- Custom user profiles with KYC, phone/email verification
- Role-based dashboards and permissions

### Product & Catalog
- Product creation, categories, multiple images, reviews, and wishlists
- Advanced search and filtering (location, price, quality, organic)
- Featured products, analytics, and price history tracking

### Orders & Logistics
- Full order lifecycle: cart, creation, delivery, completion
- Real-time order tracking and delivery management
- Transporter assignment, route optimization, GPS tracking
- Invoice generation and platform fee calculation

### Payments & Blockchain
- M-Pesa integration (planned), escrow payments, transaction management
- Blockchain smart contracts for traceability and secure transactions
- IPFS for decentralized product image storage, QR code generation

### AI Services
- Price prediction, demand forecasting, product recommendations
- Market insights and analytics

### Notifications
- SMS (Africa's Talking), email (SendGrid), push notifications, in-app messaging

### Security & Performance
- JWT authentication, input validation, CSRF/XSS protection, rate limiting
- Redis caching, database optimization, async task processing with Celery

---

## 🧩 Tech Stack
- **Backend:** Django 4.2+, Django REST Framework, Celery, Redis, PostgreSQL, Web3, python-decouple
- **Frontend:** Next.js, TypeScript, Radix UI, Tailwind CSS
- **DevOps:** Docker, environment variables, logging, deployment scripts

---

## 🏗️ Architecture Overview
- Modular Django apps: `core`, `users`, `products`, `orders`, `payments`, `blockchain`, `ai_services`, `logistics`, `notifications`
- Service layer pattern for business logic
- RESTful API endpoints documented with Swagger/OpenAPI
- Frontend consumes backend APIs for all features

---

## 🔧 Getting Started
### Backend
1. Copy `.env.example` to `.env` and configure environment variables
2. Install dependencies: `pip install -r requirements.txt`
3. Run migrations: `python manage.py migrate`
4. Create superuser: `python manage.py createsuperuser`
5. Start server: `python manage.py runserver`
6. Start Celery worker: `celery -A agriconnect worker -l info`
7. See `backend/README.md` for full details

### Frontend
1. Install dependencies: `npm install`
2. Start development server: `npm dev`
3. Build for production: `npm build`
4. See `frontend/README.md` for full details

---

## 📚 Documentation & Resources
- API docs: [Swagger UI](http://localhost:8000/api/docs/)
- Postman collection: `backend/AgriConnect_API.postman_collection.json`
- API Testing Guide: `backend/API_TESTING_GUIDE.md`
- Deployment Guide: `backend/DEPLOYMENT.md`

---

## 🧪 Testing & Quality Assurance
- Unit and integration tests: `python manage.py test`, `pytest --cov=. tests/`
- API testing via Swagger UI and Postman
- Security testing for authentication and authorization
- Coverage for authentication, products, orders, and more

---

## 🌍 Localization & Mobile Support
- Multi-language support: English, Kiswahili, Ekegusii
- API optimized for mobile apps: JSON responses, image CDN, offline support

---

## 📈 Analytics & Monitoring
- Product views, order patterns, user behavior, revenue analytics
- Performance monitoring and logging

---

## 🤝 Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

---

## Team (AgriBridge)
- **Team Lead:** Jerimia Ouko
- **Backend Developer:** Malack Arori
- **Frontend Developer:** Vincent Jossy
- **Frontend Developer:** Kimani Simeon
- **Full-Stack Developer:** Bernad Okumu

