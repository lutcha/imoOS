#!/bin/bash
# =============================================================
# ImoOS - Setup Script for Linux/Mac
# Initializes database with tenants and users for development
# =============================================================

set -e  # Exit on error

echo "========================================"
echo "ImoOS - Database Setup"
echo "========================================"
echo ""

# Check if Docker is running
echo "[1/6] Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    echo "❌ ERROR: Docker is not running!"
    echo "Please start Docker Desktop and try again."
    exit 1
fi
echo "✓ Docker is running"
echo ""

# Start services
echo "[2/6] Starting services..."
docker-compose -f docker-compose.dev.yml up -d
echo "✓ Services started"
echo ""

# Wait for database to be ready
echo "[3/6] Waiting for database to be ready..."
sleep 10
echo "✓ Database ready"
echo ""

# Run migrations
echo "[4/6] Running database migrations..."
docker-compose -f docker-compose.dev.yml exec -T web python manage.py migrate_schemas
echo "✓ Migrations completed"
echo ""

# Create demo tenant
echo "[5/6] Creating demo tenant..."
docker-compose -f docker-compose.dev.yml exec -T web python manage.py create_tenant \
    --schema=demo_promotora \
    --name="Demo Promotora" \
    --domain=demo.proptech.cv \
    --plan=pro || echo "⚠️  WARNING: Tenant creation may have failed (tenant might already exist)"

echo "✓ Demo tenant ready"
echo ""

# Create users
echo "[6/6] Creating users..."

# Create superadmin in public schema
docker-compose -f docker-compose.dev.yml exec -T web python manage.py create_superuser_public

# Create demo users in tenant schema
docker-compose -f docker-compose.dev.yml exec -T web python manage.py ensure_demo_users --tenant=demo_promotora

echo "✓ Users created"
echo ""

echo "========================================"
echo "✅ Setup Complete!"
echo "========================================"
echo ""
echo "You can now login with:"
echo ""
echo "Super Admin:"
echo "  URL: http://localhost:8001/superadmin/login"
echo "  Email: admin@proptech.cv"
echo "  Password: ImoOS2026"
echo ""
echo "Tenant User:"
echo "  URL: http://localhost:8001/login"
echo "  Email: gerente@demo.cv"
echo "  Password: Demo2026!"
echo "  Tenant Domain: demo.proptech.cv"
echo ""
echo "Backend API: http://localhost:8001"
echo "Frontend: http://localhost:3001"
echo ""
echo "To view logs: docker-compose -f docker-compose.dev.yml logs -f"
echo ""
