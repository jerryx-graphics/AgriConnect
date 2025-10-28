#!/bin/bash

# AgriConnect Backend Deployment Script
# This script handles deployment for different environments

set -e

ENVIRONMENT=${1:-development}
echo "Deploying AgriConnect backend for environment: $ENVIRONMENT"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check required tools
echo "Checking required tools..."
if ! command_exists docker; then
    echo "Error: Docker is not installed"
    exit 1
fi

if ! command_exists docker-compose; then
    echo "Error: Docker Compose is not installed"
    exit 1
fi

# Set environment file
if [ "$ENVIRONMENT" = "production" ]; then
    ENV_FILE=".env.production"
    COMPOSE_FILE="docker-compose.prod.yml"
else
    ENV_FILE=".env"
    COMPOSE_FILE="docker-compose.yml"
fi

# Check if environment file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "Error: Environment file $ENV_FILE not found"
    echo "Please copy .env.example to $ENV_FILE and configure it"
    exit 1
fi

# Create required directories
echo "Creating required directories..."
mkdir -p logs
mkdir -p media
mkdir -p staticfiles

# Set appropriate permissions
chmod 755 logs media staticfiles

# Stop existing containers
echo "Stopping existing containers..."
docker-compose -f $COMPOSE_FILE down

# Pull latest images
echo "Pulling latest images..."
docker-compose -f $COMPOSE_FILE pull

# Build application
echo "Building application..."
docker-compose -f $COMPOSE_FILE build

# Run database migrations
echo "Running database migrations..."
docker-compose -f $COMPOSE_FILE run --rm web python manage.py migrate

# Collect static files (for production)
if [ "$ENVIRONMENT" = "production" ]; then
    echo "Collecting static files..."
    docker-compose -f $COMPOSE_FILE run --rm web python manage.py collectstatic --noinput
fi

# Create superuser (only for development)
if [ "$ENVIRONMENT" = "development" ]; then
    echo "Creating superuser for development..."
    docker-compose -f $COMPOSE_FILE run --rm web python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@agriconnect.co.ke', 'admin123', role='admin')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"
fi

# Start services
echo "Starting services..."
docker-compose -f $COMPOSE_FILE up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

# Health check
echo "Performing health check..."
if curl -f http://localhost:8000/admin/ >/dev/null 2>&1; then
    echo "✅ Application is running successfully!"
    echo "📱 Admin interface: http://localhost:8000/admin/"
    echo "📚 API documentation: http://localhost:8000/api/docs/"

    if [ "$ENVIRONMENT" = "development" ]; then
        echo "🔑 Development superuser: admin/admin123"
    fi
else
    echo "❌ Health check failed. Check logs:"
    docker-compose -f $COMPOSE_FILE logs web
    exit 1
fi

# Show running containers
echo "Running containers:"
docker-compose -f $COMPOSE_FILE ps

echo "🚀 Deployment completed successfully!"

# Additional production setup instructions
if [ "$ENVIRONMENT" = "production" ]; then
    echo ""
    echo "📋 Additional production setup required:"
    echo "1. Configure SSL certificates in ./ssl/ directory"
    echo "2. Update domain names in nginx.conf"
    echo "3. Set up backup strategy for database"
    echo "4. Configure monitoring and logging"
    echo "5. Set up CI/CD pipeline"
    echo "6. Configure external storage (S3) if needed"
fi