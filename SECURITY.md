# ImoOS - Security Documentation

## 🔒 Security Hardening (Sprint 7 - Prompt 05)

### Overview

This document outlines the security measures implemented in ImoOS as part of Sprint 7 Security Hardening.

---

## ✅ Implemented Security Measures

### 1. Security Headers

#### HTTP Security Headers
```python
SECURE_BROWSER_XSS_FILTER = True              # XSS filter in browsers
SECURE_CONTENT_TYPE_NOSNIFF = True            # Prevent MIME type sniffing
X_FRAME_OPTIONS = 'DENY'                      # Prevent clickjacking
REFERRER_POLICY = 'strict-origin-when-cross-origin'
```

#### HSTS (Production Only)
```python
SECURE_HSTS_SECONDS = 31536000                # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

---

### 2. Content Security Policy (CSP)

#### CSP Configuration
```python
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "'unsafe-eval'", 'https://*.sentry.io')
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", 'https://fonts.googleapis.com')
CSP_IMG_SRC = ("'self'", 'data:', 'blob:', 'https:')
CSP_CONNECT_SRC = ("'self'", 'https://*.sentry.io', 'https://*.imos.cv')
CSP_OBJECT_SRC = ("'none'",)
CSP_BASE_URI = ("'self'",)
CSP_FORM_ACTION = ("'self'",)
```

#### Purpose
- Prevents XSS attacks by controlling resource loading
- Blocks inline scripts unless explicitly allowed
- Restricts external resource loading to trusted domains

---

### 3. Permissions Policy

#### Disabled Features
```python
PERMISSIONS_POLICY = {
    'accelerometer': [],
    'camera': [],
    'geolocation': [],
    'microphone': [],
    'payment': [],
    'usb': [],
    # ... (all sensitive features disabled)
}
```

#### Purpose
- Prevents browser features from being accessed without explicit need
- Reduces attack surface

---

### 4. CSRF Protection

#### Configuration
```python
CSRF_COOKIE_SECURE = not DEBUG                # HTTPS only in production
CSRF_COOKIE_HTTPONLY = True                   # Not accessible via JavaScript
CSRF_COOKIE_SAMESITE = 'Lax'                  # CSRF protection
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS')
```

---

### 5. Session Security

#### Configuration
```python
SESSION_COOKIE_SECURE = not DEBUG             # HTTPS only in production
SESSION_COOKIE_HTTPONLY = True                # Not accessible via JavaScript
SESSION_COOKIE_SAMESITE = 'Lax'               # CSRF protection
SESSION_COOKIE_AGE = 1209600                  # 2 weeks
SESSION_EXPIRE_AT_BROWSER_CLOSE = True        # Expire on browser close
```

---

### 6. Rate Limiting

#### API Rate Limits
```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'apps.core.throttling.TenantScopedThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',          # Anonymous users
        'user': '1000/hour',         # Authenticated users
        'tenant': '5000/hour',       # Per-tenant limit
    }
}
```

#### Public Endpoint Limits
- Lead capture: 100 requests/hour per IP
- Auth endpoints: Standard DRF throttling
- Webhook endpoints: Verified with signatures

---

### 7. Password Security

#### Password Validators
```python
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
```

#### Password Hashing
```python
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',  # Default
    'django.contrib.auth.hashers.Argon2PasswordHasher',  # If available
]
```

---

## 🛡️ Security Audit Command

### Usage

```bash
# Run security audit
python manage.py security_audit

# Generate detailed report
python manage.py security_audit --report

# Attempt auto-fix
python manage.py security_audit --fix
```

### Checks Performed

1. **Password Policies** - Validators and hashing
2. **Admin Users** - Superuser configuration
3. **Rate Limiting** - API throttling configuration
4. **Security Headers** - HTTP headers
5. **CSP Configuration** - Content Security Policy
6. **Dependencies** - Vulnerable packages (via `safety`)

---

## 🔍 Security Scanning Tools

### 1. Safety (Dependency Vulnerabilities)

```bash
# Install
pip install safety

# Scan for vulnerabilities
safety check

# Generate report
safety check --json > vulnerabilities.json
```

### 2. Bandit (Python Code Security)

```bash
# Install
pip install bandit

# Scan codebase
bandit -r apps/ config/

# Generate report
bandit -r apps/ -f html -o bandit-report.html
```

### 3. OWASP ZAP (Web Application Security)

```bash
# Run baseline scan
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t http://localhost:8000/

# Full scan
docker run -t owasp/zap2docker-stable zap-full-scan.py \
  -t http://localhost:8000/
```

---

## 📋 Security Checklist

### Production Deployment

- [ ] `DEBUG = False`
- [ ] `SECRET_KEY` is unique and secure (50+ characters)
- [ ] `ALLOWED_HOSTS` is configured
- [ ] HTTPS is enforced (`SECURE_SSL_REDIRECT = True`)
- [ ] HSTS is configured
- [ ] CSP headers are set
- [ ] Security headers are present
- [ ] Rate limiting is active
- [ ] Database credentials are secure
- [ ] API keys are in environment variables
- [ ] `safety check` passes
- [ ] `bandit` scan passes
- [ ] Superuser passwords are strong

### Development

- [ ] `.env` file is in `.gitignore`
- [ ] Debug toolbar is only enabled in development
- [ ] CORS is configured for frontend domain
- [ ] Test data doesn't include real user data

---

## 🚨 Security Incident Response

### If a vulnerability is discovered:

1. **Immediate Actions**
   - Rotate affected credentials
   - Enable additional logging
   - Notify security team

2. **Investigation**
   - Review logs for suspicious activity
   - Check affected systems
   - Document findings

3. **Remediation**
   - Patch vulnerability
   - Update dependencies
   - Deploy security fix

4. **Post-Incident**
   - Review what happened
   - Update security procedures
   - Implement additional controls

---

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Django Security Documentation](https://docs.djangoproject.com/en/stable/topics/security/)
- [Content Security Policy Guide](https://content-security-policy.com/)
- [Mozilla Security Headers](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers)

---

**Last Updated:** Sprint 7 - Prompt 05  
**Security Status:** ✅ Hardened
