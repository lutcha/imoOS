#!/bin/bash
# ImoOS Security Scan Script
# Sprint 7 - Prompt 05: Security Hardening
# 
# Usage: ./scripts/security_scan.sh

set -e

echo "============================================================"
echo "🔒 ImoOS Security Scan"
echo "============================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counter
ISSUES=0
WARNINGS=0

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
        ((ISSUES++))
    fi
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
}

echo "1. Checking Django Security Settings..."
echo "------------------------------------------------------------"

# Check DEBUG is False in production
if [ "$DJANGO_SETTINGS_MODULE" = "config.settings.production" ]; then
    if [ "$DEBUG" = "True" ]; then
        print_status 1 "DEBUG is enabled in production!"
    else
        print_status 0 "DEBUG is disabled"
    fi
fi

# Check SECRET_KEY length
if [ ${#SECRET_KEY} -lt 50 ]; then
    print_warning "SECRET_KEY is shorter than 50 characters"
else
    print_status 0 "SECRET_KEY length is adequate"
fi

echo ""
echo "2. Running Safety Check (Dependency Vulnerabilities)..."
echo "------------------------------------------------------------"

if command -v safety &> /dev/null; then
    safety check --continue-on-error || print_warning "Vulnerable dependencies found"
else
    print_warning "Safety not installed. Install with: pip install safety"
fi

echo ""
echo "3. Running Bandit (Python Security Linter)..."
echo "------------------------------------------------------------"

if command -v bandit &> /dev/null; then
    bandit -r apps/ config/ -ll || print_warning "Bandit found issues"
else
    print_warning "Bandit not installed. Install with: pip install bandit"
fi

echo ""
echo "4. Checking File Permissions..."
echo "------------------------------------------------------------"

# Check .env file permissions
if [ -f ".env" ]; then
    PERMS=$(stat -c %a .env 2>/dev/null || stat -f %A .env 2>/dev/null)
    if [ "$PERMS" != "600" ]; then
        print_warning ".env file permissions should be 600 (current: $PERMS)"
    else
        print_status 0 ".env file permissions are secure"
    fi
fi

echo ""
echo "5. Running Django Security Audit..."
echo "------------------------------------------------------------"

if command -v python &> /dev/null; then
    python manage.py security_audit --report || print_warning "Security audit found issues"
fi

echo ""
echo "============================================================"
echo "Security Scan Summary"
echo "============================================================"
echo -e "  Issues:   ${RED}$ISSUES${NC}"
echo -e "  Warnings: ${YELLOW}$WARNINGS${NC}"
echo "============================================================"

if [ $ISSUES -gt 0 ]; then
    echo -e "${RED}⚠️  Security issues found! Please review and fix.${NC}"
    exit 1
else
    echo -e "${GREEN}✅ No critical security issues found!${NC}"
    exit 0
fi
