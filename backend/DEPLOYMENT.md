# AgriConnect Backend Deployment Guide

## 🚀 Quick Start

### Development Setup

1. **Clone and setup environment:**
```bash
git clone <repository>
cd AgriConnect/backend
cp .env.example .env
```

2. **Configure environment variables in `.env`:**
```bash
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=agriconnect
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

3. **Deploy with Docker:**
```bash
chmod +x deploy.sh
./deploy.sh development
```

4. **Access the application:**
- API Documentation: http://localhost:8000/api/docs/
- Admin Interface: http://localhost:8000/admin/
- Login: admin/admin123 (development only)

### Production Deployment

1. **Setup production environment:**
```bash
cp .env.example .env.production
# Configure production variables
```

2. **Deploy to production:**
```bash
./deploy.sh production
```

## 📋 Environment Configuration

### Required Environment Variables

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_NAME=agriconnect
DB_USER=postgres
DB_PASSWORD=your-secure-password
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# Email (SendGrid)
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key

# SMS (Africa's Talking)
AFRICASTALKING_USERNAME=your-username
AFRICASTALKING_API_KEY=your-api-key

# M-Pesa (Daraja API)
MPESA_CONSUMER_KEY=your-consumer-key
MPESA_CONSUMER_SECRET=your-consumer-secret
MPESA_SHORTCODE=174379
MPESA_PASSKEY=your-passkey

# Blockchain
WEB3_PROVIDER_URL=your-infura-url
PRIVATE_KEY=your-private-key
CONTRACT_ADDRESS=your-contract-address
```

## 🔧 Manual Installation (Alternative)

### Prerequisites
- Python 3.11+
- PostgreSQL 12+
- Redis 6+

### Setup Steps

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Setup database:**
```bash
createdb agriconnect
python manage.py migrate
```

3. **Create superuser:**
```bash
python manage.py createsuperuser
```

4. **Run development server:**
```bash
python manage.py runserver
```

5. **Start Celery (separate terminal):**
```bash
celery -A agriconnect worker -l info
```

## 🐳 Docker Services

### Development Stack
- **web**: Django application server
- **db**: PostgreSQL database
- **redis**: Redis cache and message broker
- **celery**: Background task worker
- **celery-beat**: Periodic task scheduler

### Production Stack
- **nginx**: Reverse proxy and static file server
- **web**: Gunicorn WSGI server
- **db**: PostgreSQL with SSL
- **redis**: Redis with persistence
- **celery**: Production worker configuration
- **celery-beat**: Production scheduler

## 📊 Monitoring & Maintenance

### Health Checks
```bash
# Check application health
curl http://localhost:8000/admin/

# Check container status
docker-compose ps

# View logs
docker-compose logs web
docker-compose logs celery
```

### Database Backup
```bash
# Backup database
docker-compose exec db pg_dump -U postgres agriconnect > backup.sql

# Restore database
docker-compose exec -T db psql -U postgres agriconnect < backup.sql
```

### SSL Certificate Setup (Production)

1. **Obtain SSL certificates:**
```bash
# Using Let's Encrypt
certbot certonly --webroot -w /var/www/html -d agriconnect.co.ke
```

2. **Copy certificates:**
```bash
mkdir ssl
cp /etc/letsencrypt/live/agriconnect.co.ke/fullchain.pem ssl/agriconnect.crt
cp /etc/letsencrypt/live/agriconnect.co.ke/privkey.pem ssl/agriconnect.key
```

## 🔐 Security Checklist

### Production Security
- [ ] Use strong, unique SECRET_KEY
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS
- [ ] Enable HTTPS with valid SSL certificates
- [ ] Use secure database passwords
- [ ] Configure firewall rules
- [ ] Set up regular security updates
- [ ] Enable database SSL connections
- [ ] Configure proper backup encryption

### Application Security
- [ ] JWT tokens properly configured
- [ ] Rate limiting enabled
- [ ] Input validation implemented
- [ ] File upload security enabled
- [ ] CORS properly configured
- [ ] Security headers configured in Nginx
- [ ] Database queries optimized against injection

## 🚨 Troubleshooting

### Common Issues

**Database Connection Errors:**
```bash
# Check database service
docker-compose logs db

# Reset database
docker-compose down
docker volume rm agriconnect_postgres_data
docker-compose up -d
```

**Permission Errors:**
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod -R 755 media staticfiles logs
```

**Memory Issues:**
```bash
# Increase Docker memory limits
# Edit docker-compose.yml and add:
services:
  web:
    deploy:
      resources:
        limits:
          memory: 1G
```

### Performance Optimization

**Database Optimization:**
```bash
# Run database analysis
docker-compose exec db psql -U postgres -d agriconnect -c "ANALYZE;"

# Check slow queries
docker-compose exec db psql -U postgres -d agriconnect -c "
SELECT query, mean_time, calls
FROM pg_stat_statements
ORDER BY mean_time DESC LIMIT 10;
"
```

**Redis Memory:**
```bash
# Check Redis memory usage
docker-compose exec redis redis-cli info memory
```

## 📈 Scaling Considerations

### Horizontal Scaling
- Use multiple web worker containers
- Implement database read replicas
- Use Redis Cluster for high availability
- Consider CDN for static files

### Vertical Scaling
- Increase container memory/CPU limits
- Optimize database queries
- Use database connection pooling
- Implement caching strategies

## 🔄 CI/CD Integration

### GitHub Actions Example
```yaml
name: Deploy to Production
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to server
        run: |
          ssh user@server 'cd /app && git pull && ./deploy.sh production'
```

## 📞 Support

For deployment issues:
- Check logs: `docker-compose logs`
- Review configuration: Environment variables
- Database connectivity: Network settings
- External services: API credentials

Contact: tech@agriconnect.co.ke