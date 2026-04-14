@echo off
REM =============================================================
REM ImoOS - Setup Script for Windows
REM Initializes database with tenants and users for development
REM =============================================================

echo ========================================
echo ImoOS - Database Setup
echo ========================================
echo.

REM Check if Docker is running
echo [1/6] Checking Docker...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)
echo ✓ Docker is running
echo.

REM Start services
echo [2/6] Starting services...
docker-compose -f docker-compose.dev.yml up -d
if %errorlevel% neq 0 (
    echo ERROR: Failed to start services
    pause
    exit /b 1
)
echo ✓ Services started
echo.

REM Wait for database to be ready
echo [3/6] Waiting for database to be ready...
timeout /t 10 /nobreak >nul
echo ✓ Database ready
echo.

REM Run migrations
echo [4/6] Running database migrations...
docker-compose -f docker-compose.dev.yml exec -T web python manage.py migrate_schemas
if %errorlevel% neq 0 (
    echo ERROR: Migrations failed
    pause
    exit /b 1
)
echo ✓ Migrations completed
echo.

REM Create demo tenant
echo [5/6] Creating demo tenant...
docker-compose -f docker-compose.dev.yml exec -T web python manage.py create_tenant ^
    --schema=demo_promotora ^
    --name="Demo Promotora" ^
    --domain=demo.proptech.cv ^
    --plan=pro

if %errorlevel% neq 0 (
    echo WARNING: Tenant creation may have failed (tenant might already exist)
    echo Continuing...
)
echo ✓ Demo tenant ready
echo.

REM Create users
echo [6/6] Creating users...

REM Create superadmin in public schema
docker-compose -f docker-compose.dev.yml exec -T web python manage.py create_superuser_public

REM Create demo users in tenant schema
docker-compose -f docker-compose.dev.yml exec -T web python manage.py ensure_demo_users --tenant=demo_promotora

echo ✓ Users created
echo.

echo ========================================
echo ✅ Setup Complete!
echo ========================================
echo.
echo You can now login with:
echo.
echo Super Admin:
echo   URL: http://localhost:8001/superadmin/login
echo   Email: admin@proptech.cv
echo   Password: ImoOS2026
echo.
echo Tenant User:
echo   URL: http://localhost:8001/login
echo   Email: gerente@demo.cv
echo   Password: Demo2026!
echo   Tenant Domain: demo.proptech.cv
echo.
echo Backend API: http://localhost:8001
echo Frontend: http://localhost:3001
echo.
echo To view logs: docker-compose -f docker-compose.dev.yml logs -f
echo.
pause
