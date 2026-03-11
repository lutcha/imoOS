#!/usr/bin/env bash
# =============================================================
# ImoOS — Pre-push secrets & safety checklist
# Run before: git push origin develop
# =============================================================
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0

fail() { echo -e "${RED}[FAIL]${NC} $1"; ERRORS=$((ERRORS + 1)); }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
ok()   { echo -e "${GREEN}[ OK ]${NC} $1"; }

echo "============================================="
echo "  ImoOS Pre-Push Safety Checklist"
echo "============================================="

# 1. .env not staged
if git diff --cached --name-only | grep -qE '^\.env$'; then
    fail ".env is staged — NEVER commit secrets!"
else
    ok ".env not staged"
fi

# 2. No hardcoded secrets patterns
SECRET_PATTERNS='(SECRET_KEY\s*=\s*["\x27][^$][^"\x27]{10,}|password\s*=\s*["\x27][^"\x27]{6,}|api_key\s*=\s*["\x27][^"\x27]{10,})'
if git diff --cached -i | grep -qiE "$SECRET_PATTERNS"; then
    fail "Possible hardcoded secret detected in staged changes — review diff!"
else
    ok "No hardcoded secrets detected"
fi

# 3. DEBUG=True not in any settings except development.py
if grep -r "DEBUG\s*=\s*True" config/settings/ --include="*.py" \
   | grep -v development.py | grep -v testing.py; then
    fail "DEBUG=True found outside development/testing settings"
else
    ok "DEBUG=True only in dev/test settings"
fi

# 4. .gitignore covers .env
if grep -q "^\.env$" .gitignore 2>/dev/null; then
    ok ".env in .gitignore"
else
    fail ".env not in .gitignore"
fi

# 5. No print() debug statements left in apps/
PRINT_COUNT=$(git diff --cached -- 'apps/**/*.py' | grep '^+' | grep -c 'print(' || true)
if [ "$PRINT_COUNT" -gt 0 ]; then
    warn "$PRINT_COUNT print() statement(s) added — use logger instead"
else
    ok "No new print() statements"
fi

# 6. CI lint passes locally (fast check)
if command -v black &>/dev/null; then
    if black --check apps/ config/ tests/ -q 2>/dev/null; then
        ok "black formatting OK"
    else
        fail "black formatting issues — run: make format"
    fi
else
    warn "black not installed locally — CI will catch formatting issues"
fi

echo "============================================="
if [ "$ERRORS" -gt 0 ]; then
    echo -e "${RED}$ERRORS error(s) found. Fix before pushing.${NC}"
    exit 1
else
    echo -e "${GREEN}All checks passed. Safe to push.${NC}"
fi
