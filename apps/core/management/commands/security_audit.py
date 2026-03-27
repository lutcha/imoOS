"""
Security Audit Management Command - ImoOS
Sprint 7 - Prompt 05: Security Hardening

Usage:
    python manage.py security_audit
    python manage.py security_audit --report
"""
import json
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Count
import subprocess
import sys


class Command(BaseCommand):
    help = 'Run security audit checks for ImoOS platform'

    def add_arguments(self, parser):
        parser.add_argument(
            '--report',
            action='store_true',
            help='Generate detailed security report',
        )
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Attempt to fix common issues',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔒 ImoOS Security Audit\n'))
        
        report = options['report']
        auto_fix = options['fix']
        
        issues = []
        warnings = []
        passed = []
        
        # Run all security checks
        issues.extend(self.check_password_policies())
        issues.extend(self.check_admin_users())
        issues.extend(self.check_rate_limiting())
        issues.extend(self.check_security_headers())
        issues.extend(self.check_csp_config())
        issues.extend(self.check_dependencies())
        
        # Display results
        self.display_results(issues, warnings, passed, report)
        
        if issues:
            raise CommandError(f'Security audit found {len(issues)} issues')

    def check_password_policies(self):
        """Check password validation and hashing."""
        issues = []
        
        # Check AUTH_PASSWORD_VALIDATORS
        validators = getattr(settings, 'AUTH_PASSWORD_VALIDATORS', [])
        if len(validators) < 4:
            issues.append({
                'severity': 'HIGH',
                'category': 'Authentication',
                'issue': 'Insufficient password validators',
                'recommendation': 'Add all 4 default Django password validators',
            })
        
        # Check password hashers
        hashers = getattr(settings, 'PASSWORD_HASHERS', [])
        if 'PBKDF2' not in str(hashers) and 'Argon2' not in str(hashers):
            issues.append({
                'severity': 'MEDIUM',
                'category': 'Authentication',
                'issue': 'Weak password hashing algorithm',
                'recommendation': 'Use PBKDF2 or Argon2 for password hashing',
            })
        
        return issues

    def check_admin_users(self):
        """Check for superuser accounts."""
        issues = []
        User = get_user_model()
        
        # Check for default admin passwords
        superusers = User.objects.filter(is_superuser=True, is_staff=True)
        
        if superusers.count() == 0:
            issues.append({
                'severity': 'CRITICAL',
                'category': 'Authentication',
                'issue': 'No superuser accounts found',
                'recommendation': 'Create at least one superuser account',
            })
        
        # Check for users with weak passwords (common patterns)
        weak_passwords = ['admin', 'password', '123456', 'imos', 'demo']
        # Note: Can't check actual passwords, but can warn about policy
        
        return issues

    def check_rate_limiting(self):
        """Check rate limiting configuration."""
        issues = []
        
        # Check if django-ratelimit is configured
        if 'apps.core.throttling' not in str(settings.INSTALLED_APPS):
            issues.append({
                'severity': 'MEDIUM',
                'category': 'Rate Limiting',
                'issue': 'Rate limiting may not be properly configured',
                'recommendation': 'Ensure apps.core.throttling is in INSTALLED_APPS',
            })
        
        # Check REST framework throttle settings
        rest_framework = getattr(settings, 'REST_FRAMEWORK', {})
        throttle_classes = rest_framework.get('DEFAULT_THROTTLE_CLASSES', [])
        
        if not throttle_classes:
            issues.append({
                'severity': 'HIGH',
                'category': 'Rate Limiting',
                'issue': 'No API rate limiting configured',
                'recommendation': 'Configure DEFAULT_THROTTLE_CLASSES in REST_FRAMEWORK settings',
            })
        
        return issues

    def check_security_headers(self):
        """Check security headers configuration."""
        issues = []
        
        # Check X_FRAME_OPTIONS
        if not getattr(settings, 'X_FRAME_OPTIONS', None):
            issues.append({
                'severity': 'MEDIUM',
                'category': 'Security Headers',
                'issue': 'X_FRAME_OPTIONS not configured',
                'recommendation': 'Set X_FRAME_OPTIONS = "DENY" to prevent clickjacking',
            })
        
        # Check SECURE_CONTENT_TYPE_NOSNIFF
        if not getattr(settings, 'SECURE_CONTENT_TYPE_NOSNIFF', None):
            issues.append({
                'severity': 'LOW',
                'category': 'Security Headers',
                'issue': 'SECURE_CONTENT_TYPE_NOSNIFF not configured',
                'recommendation': 'Set to True to prevent MIME type sniffing',
            })
        
        # Check SECURE_BROWSER_XSS_FILTER
        if not getattr(settings, 'SECURE_BROWSER_XSS_FILTER', None):
            issues.append({
                'severity': 'LOW',
                'category': 'Security Headers',
                'issue': 'SECURE_BROWSER_XSS_FILTER not configured',
                'recommendation': 'Set to True for XSS protection',
            })
        
        # Check HSTS (production only)
        if not settings.DEBUG:
            if not getattr(settings, 'SECURE_HSTS_SECONDS', 0):
                issues.append({
                    'severity': 'HIGH',
                    'category': 'Security Headers',
                    'issue': 'HSTS not configured in production',
                    'recommendation': 'Set SECURE_HSTS_SECONDS = 31536000 (1 year)',
                })
        
        return issues

    def check_csp_config(self):
        """Check Content Security Policy configuration."""
        issues = []
        
        # Check if django-csp is installed
        if 'csp' not in settings.INSTALLED_APPS:
            issues.append({
                'severity': 'HIGH',
                'category': 'Content Security Policy',
                'issue': 'django-csp not installed',
                'recommendation': 'Install and configure django-csp for CSP headers',
            })
            return issues
        
        # Check CSP configuration
        csp_config = getattr(settings, 'CSP_DEFAULT_SRC', None)
        if not csp_config:
            issues.append({
                'severity': 'MEDIUM',
                'category': 'Content Security Policy',
                'issue': 'CSP_DEFAULT_SRC not configured',
                'recommendation': 'Configure CSP_DEFAULT_SRC = ("\'self\'",)',
            })
        
        # Check for unsafe-inline in script-src
        csp_script_src = getattr(settings, 'CSP_SCRIPT_SRC', [])
        if "'unsafe-inline'" in str(csp_script_src) and not settings.DEBUG:
            issues.append({
                'severity': 'MEDIUM',
                'category': 'Content Security Policy',
                'issue': "'unsafe-inline' in CSP_SCRIPT_SRC (production)",
                'recommendation': 'Remove 'unsafe-inline' and use nonces or hashes',
            })
        
        return issues

    def check_dependencies(self):
        """Check for vulnerable dependencies."""
        issues = []
        
        try:
            # Run safety check
            result = subprocess.run(
                ['safety', 'check', '--json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                vulnerabilities = json.loads(result.stdout)
                
                if vulnerabilities:
                    issues.append({
                        'severity': 'CRITICAL',
                        'category': 'Dependencies',
                        'issue': f'{len(vulnerabilities)} vulnerable dependencies found',
                        'recommendation': 'Run "safety check" and update vulnerable packages',
                        'details': vulnerabilities[:5],  # First 5 vulnerabilities
                    })
        except FileNotFoundError:
            # Safety not installed
            issues.append({
                'severity': 'LOW',
                'category': 'Dependencies',
                'issue': 'Safety not installed for vulnerability scanning',
                'recommendation': 'Install safety: pip install safety',
            })
        except subprocess.TimeoutExpired:
            issues.append({
                'severity': 'LOW',
                'category': 'Dependencies',
                'issue': 'Dependency check timed out',
                'recommendation': 'Run "safety check" manually',
            })
        except Exception as e:
            issues.append({
                'severity': 'LOW',
                'category': 'Dependencies',
                'issue': f'Could not check dependencies: {str(e)}',
                'recommendation': 'Run "pip check" manually',
            })
        
        return issues

    def display_results(self, issues, warnings, passed, detailed=False):
        """Display audit results."""
        
        # Summary
        critical = len([i for i in issues if i['severity'] == 'CRITICAL'])
        high = len([i for i in issues if i['severity'] == 'HIGH'])
        medium = len([i for i in issues if i['severity'] == 'MEDIUM'])
        low = len([i for i in issues if i['severity'] == 'LOW'])
        
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write('SECURITY AUDIT SUMMARY')
        self.stdout.write('=' * 60)
        self.stdout.write(f'  Critical: {critical}')
        self.stdout.write(f'  High:     {high}')
        self.stdout.write(f'  Medium:   {medium}')
        self.stdout.write(f'  Low:      {low}')
        self.stdout.write('=' * 60 + '\n')
        
        if detailed:
            # Group by severity
            for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
                severity_issues = [i for i in issues if i['severity'] == severity]
                
                if severity_issues:
                    self.stdout.write(self.style.ERROR(f'\n{severity} Issues:'))
                    
                    for issue in severity_issues:
                        self.stdout.write(f"\n  [{issue['category']}] {issue['issue']}")
                        self.stdout.write(f'    Recommendation: {issue["recommendation"]}')
                        
                        if 'details' in issue:
                            self.stdout.write(f'    Details: {json.dumps(issue["details"], indent=2)}')
        
        if not issues:
            self.stdout.write(self.style.SUCCESS('\n✅ No security issues found!'))
        else:
            self.stdout.write(self.style.WARNING(
                f'\n⚠️  Found {len(issues)} security issue(s) that need attention'
            ))
